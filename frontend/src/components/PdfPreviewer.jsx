import React, { useEffect, useRef, useState, useCallback } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, AlertCircle, RefreshCw, FileText } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import pdfWorker from 'pdfjs-dist/build/pdf.worker.min.js?url';

if (typeof window !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;
}

export default function PdfPreviewer({ pdfUrl, onRefresh, title = "PDF Preview" }) {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.15);
  const [pdfDoc, setPdfDoc] = useState(null);
  const renderTasksRef = useRef([]);

  // Load PDF Document via ArrayBuffer to eliminate worker fetch CORS/blob restrictions
  useEffect(() => {
    if (!pdfUrl) {
      setPdfDoc(null);
      setNumPages(0);
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    (async () => {
      try {
        let buffer;
        if (typeof pdfUrl === 'string') {
          const resp = await fetch(pdfUrl);
          if (!resp.ok) {
            throw new Error(`Failed to fetch PDF (status ${resp.status})`);
          }
          buffer = await resp.arrayBuffer();
        } else if (pdfUrl instanceof Blob) {
          buffer = await pdfUrl.arrayBuffer();
        } else if (pdfUrl instanceof ArrayBuffer) {
          buffer = pdfUrl;
        } else if (ArrayBuffer.isView(pdfUrl)) {
          buffer = pdfUrl.buffer;
        }

        if (!isMounted) return;

        const loadingTask = pdfjsLib.getDocument({
          data: new Uint8Array(buffer),
          cMapPacked: true,
        });

        const doc = await loadingTask.promise;
        if (!isMounted) {
          doc.destroy();
          return;
        }

        setPdfDoc(doc);
        setNumPages(doc.numPages);
        setLoading(false);
      } catch (err) {
        if (!isMounted) return;
        console.error('PdfPreviewer document loading failed:', err);
        setError('Failed to load PDF preview. Click retry to refresh.');
        setLoading(false);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, [pdfUrl]);

  // Cancel any active rendering tasks
  const cancelRenderTasks = () => {
    renderTasksRef.current.forEach((task) => {
      try {
        task.cancel();
      } catch {
        // ignore cancellation
      }
    });
    renderTasksRef.current = [];
  };

  // Render all pages
  const renderPages = useCallback(async () => {
    if (!pdfDoc || !containerRef.current) return;

    cancelRenderTasks();
    const container = containerRef.current;
    container.innerHTML = '';

    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
      try {
        const page = await pdfDoc.getPage(pageNum);
        const viewport = page.getViewport({ scale });

        // Outer Page Wrapper
        const pageWrapper = document.createElement('div');
        pageWrapper.className = 'pdf-page-wrapper relative mb-5 shadow-lg bg-white border-2 border-charcoal mx-auto';
        pageWrapper.style.width = `${Math.floor(viewport.width)}px`;
        pageWrapper.style.height = `${Math.floor(viewport.height)}px`;
        pageWrapper.style.position = 'relative';

        // Canvas for PDF graphics
        const canvas = document.createElement('canvas');
        canvas.className = 'block';
        const outputScale = window.devicePixelRatio || 1;
        canvas.width = Math.floor(viewport.width * outputScale);
        canvas.height = Math.floor(viewport.height * outputScale);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        const ctx = canvas.getContext('2d');
        ctx.scale(outputScale, outputScale);
        pageWrapper.appendChild(canvas);

        // Annotation Layer Div
        const annotationLayerDiv = document.createElement('div');
        annotationLayerDiv.className = 'annotationLayer';
        annotationLayerDiv.style.width = `${Math.floor(viewport.width)}px`;
        annotationLayerDiv.style.height = `${Math.floor(viewport.height)}px`;
        annotationLayerDiv.style.position = 'absolute';
        annotationLayerDiv.style.top = '0';
        annotationLayerDiv.style.left = '0';
        annotationLayerDiv.style.right = '0';
        annotationLayerDiv.style.bottom = '0';
        annotationLayerDiv.style.pointerEvents = 'none';
        pageWrapper.appendChild(annotationLayerDiv);

        container.appendChild(pageWrapper);

        // Render PDF page canvas graphics
        const renderTask = page.render({
          canvasContext: ctx,
          viewport: viewport,
        });
        renderTasksRef.current.push(renderTask);
        await renderTask.promise;

        // Fetch link annotations and build interactive links
        const annotations = await page.getAnnotations();
        if (annotations && annotations.length > 0) {
          const linkService = {
            getDestinationHash: (dest) => '#',
            getAnchorUrl: (hash) => hash,
            setHash: () => {},
            executeNamedAction: () => {},
            addLinkAttributes: (link, url) => {
              link.href = url;
              link.target = '_blank';
              link.rel = 'noopener noreferrer';
            },
          };

          // Try official AnnotationLayer instance render
          try {
            if (typeof pdfjsLib.AnnotationLayer === 'function') {
              const layer = new pdfjsLib.AnnotationLayer({
                div: annotationLayerDiv,
                accessibilityManager: null,
                annotationCanvasMap: null,
                l10n: null,
                page: page,
                viewport: viewport.clone({ dontFlip: true }),
              });
              await layer.render({
                annotations: annotations,
                linkService: linkService,
                renderInteractiveForms: false,
              });
            }
          } catch (layerErr) {
            console.warn('PDF.js AnnotationLayer.render error, using fallback overlay:', layerErr);
          }

          // Build explicit link overlay elements to guarantee 100% reliable yellow hover highlight
          annotations.forEach((anno) => {
            if (anno.subtype === 'Link' && (anno.url || anno.unsafeUrl)) {
              const url = anno.url || anno.unsafeUrl;
              const [x1, y1, x2, y2] = viewport.convertToViewportRectangle(anno.rect);
              const left = Math.min(x1, x2);
              const top = Math.min(y1, y2);
              const width = Math.max(Math.abs(x2 - x1), 10);
              const height = Math.max(Math.abs(y2 - y1), 8);

              const linkAnchor = document.createElement('a');
              linkAnchor.href = url;
              linkAnchor.target = '_blank';
              linkAnchor.rel = 'noopener noreferrer';
              linkAnchor.className = 'pdf-interactive-link-overlay';
              linkAnchor.style.position = 'absolute';
              linkAnchor.style.left = `${left}px`;
              linkAnchor.style.top = `${top}px`;
              linkAnchor.style.width = `${width}px`;
              linkAnchor.style.height = `${height}px`;
              linkAnchor.style.display = 'block';
              linkAnchor.style.pointerEvents = 'auto';
              linkAnchor.style.zIndex = '15';
              linkAnchor.style.cursor = 'pointer';
              linkAnchor.title = url;

              pageWrapper.appendChild(linkAnchor);
            }
          });
        }
      } catch (err) {
        if (err?.name === 'RenderingCancelledException') {
          break;
        }
        console.error(`Page ${pageNum} render error:`, err);
      }
    }
  }, [pdfDoc, scale]);

  useEffect(() => {
    renderPages();
    return () => {
      cancelRenderTasks();
    };
  }, [renderPages]);

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.15, 2.0));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.15, 0.6));
  const handleResetZoom = () => setScale(1.15);

  return (
    <div className="pdf-previewer-root flex flex-col h-full bg-stone-100 border-2 border-charcoal">
      {/* Neo-brutal Viewer Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-2.5 sm:px-3 py-2 bg-cream border-b-2 border-charcoal text-xs font-mono select-none">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-charcoal" />
          <span className="font-bold text-charcoal">{title}</span>
          {numPages > 0 && (
            <span className="text-[11px] text-charcoal bg-white px-2 py-0.5 border border-charcoal">
              {numPages} {numPages === 1 ? 'page' : 'pages'}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-1 sm:space-x-2">
          <button
            type="button"
            onClick={handleZoomOut}
            disabled={scale <= 0.6}
            className="p-1 border border-charcoal bg-white hover:bg-cream active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-40 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5 text-charcoal" />
          </button>
          <span className="min-w-[42px] text-center text-[11px] font-bold">
            {Math.round(scale * 100)}%
          </span>
          <button
            type="button"
            onClick={handleZoomIn}
            disabled={scale >= 2.0}
            className="p-1 border border-charcoal bg-white hover:bg-cream active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-40 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5 text-charcoal" />
          </button>
          <button
            type="button"
            onClick={handleResetZoom}
            className="p-1 border border-charcoal bg-white hover:bg-cream active:translate-x-0.5 active:translate-y-0.5 transition-colors text-[11px] font-bold px-1.5"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5 text-charcoal" />
          </button>
          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              className="p-1 border border-charcoal bg-white hover:bg-cream active:translate-x-0.5 active:translate-y-0.5 transition-colors"
              title="Refresh Preview"
            >
              <RefreshCw className="w-3.5 h-3.5 text-charcoal" />
            </button>
          )}
        </div>
      </div>

      {/* Main Viewport Container */}
      <div className="relative flex-1 overflow-auto p-4 flex justify-center bg-stone-100 min-h-[640px] max-h-[820px]">
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 z-30 space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-charcoal border-t-transparent" />
            <span className="text-xs font-mono font-bold text-charcoal">Rendering Interactive PDF Canvas...</span>
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center justify-center p-6 text-center space-y-2 max-w-md m-auto">
            <AlertCircle className="w-8 h-8 text-rose-600" />
            <p className="text-xs font-mono text-rose-700">{error}</p>
            {onRefresh && (
              <button
                type="button"
                onClick={onRefresh}
                className="btn-primary text-xs py-1 px-3 mt-2"
              >
                Retry Loading
              </button>
            )}
          </div>
        )}

        <div ref={containerRef} className="pdf-previewer-canvas-container w-full flex flex-col items-center" />
      </div>

      {/* Scoped CSS for PDF.js annotation layer & vibrant yellow link hover highlighting */}
      <style>{`
        .pdf-previewer-canvas-container .pdf-page-wrapper {
          position: relative !important;
        }
        .pdf-previewer-canvas-container .annotationLayer {
          position: absolute !important;
          top: 0 !important;
          left: 0 !important;
          right: 0 !important;
          bottom: 0 !important;
          pointer-events: none !important;
          overflow: hidden !important;
        }
        .pdf-previewer-canvas-container .annotationLayer section {
          position: absolute !important;
          text-align: initial !important;
          pointer-events: auto !important;
          box-sizing: border-box !important;
        }
        .pdf-previewer-canvas-container .annotationLayer .linkAnnotation > a {
          position: absolute !important;
          font-size: 1em !important;
          top: 0 !important;
          left: 0 !important;
          width: 100% !important;
          height: 100% !important;
          cursor: pointer !important;
          pointer-events: auto !important;
        }
        /* Vibrant Yellow Neo-Brutal Link Hover Highlighting for BOTH standard and overlay anchors */
        .pdf-previewer-canvas-container .pdf-interactive-link-overlay,
        .pdf-previewer-canvas-container .annotationLayer .linkAnnotation > a {
          background-color: transparent !important;
          border-radius: 2px !important;
          transition: background-color 0.12s ease-in-out, box-shadow 0.12s ease-in-out !important;
        }
        .pdf-previewer-canvas-container .pdf-interactive-link-overlay:hover,
        .pdf-previewer-canvas-container .annotationLayer .linkAnnotation > a:hover,
        .pdf-previewer-canvas-container .annotationLayer section.linkAnnotation:hover {
          background-color: rgba(254, 240, 138, 0.75) !important; /* solid vibrant yellow */
          background: rgba(254, 240, 138, 0.75) !important;
          outline: 2px dashed #CA8A04 !important; /* amber-600 border */
          box-shadow: 0 0 0 2px rgba(254, 240, 138, 0.8) !important;
          cursor: pointer !important;
        }
      `}</style>
    </div>
  );
}
