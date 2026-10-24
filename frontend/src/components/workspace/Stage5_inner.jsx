      {currentStep === 5 && (
        <div className="space-y-6 font-mono">
          {!activeTailoredResume ? (
            <div className="card-brutal text-center py-12 space-y-4">
              <p className="text-xs text-charcoal-muted">
                No tailored resume selected. Please generate a tailored draft in
                Stage 4 first.
              </p>
              <button
                onClick={() => setCurrentStep(4)}
                className="btn-secondary text-xs"
              >
                â† Return to Stage 4: Tailor Resume
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Stage 5 Top Control Bar */}
              <div className="card-brutal bg-white p-4 flex flex-wrap items-center justify-between gap-4 border-2 border-charcoal shadow-brutal-sm">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-bold uppercase text-charcoal tracking-wider">
                    Target: {activeJob?.title} (v
                    {activeTailoredResume.version_number})
                  </span>
                  <span
                    className={`badge-tag ${
                      activeTailoredResume.status === "final"
                        ? "bg-emerald-50 text-emerald-900 border-emerald-600"
                        : "bg-amber-50 text-amber-900 border-amber-600"
                    }`}
                  >
                    {activeTailoredResume.status.toUpperCase()}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {!pdfArtifact ? (
                    <button
                      onClick={handleGeneratePdf}
                      disabled={pdfLoading}
                      className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                    >
                      {pdfLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                          <span>Compiling LaTeX...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Compile ATS PDF</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={handleDownloadPdf}
                        disabled={downloadingPdf}
                        className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                      >
                        {downloadingPdf ? (
                          <>
                            <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent" />
                            <span>Downloading...</span>
                          </>
                        ) : (
                          <>
                            <Download className="w-3.5 h-3.5 text-white" />
                            <span>Download PDF</span>
                          </>
                        )}
                      </button>

                      {!appLogged ? (
                        <button
                          type="button"
                          onClick={handleLogApplication}
                          disabled={loggingApp || !activeJob}
                          className="btn-secondary text-xs flex items-center space-x-1.5 py-1.5 px-3"
                          title="Log this application in your Applications tracker"
                        >
                          {loggingApp ? (
                            <>
                              <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-charcoal border-t-transparent" />
                              <span>Logging...</span>
                            </>
                          ) : (
                            <>
                              <Briefcase className="w-3.5 h-3.5" />
                              <span>Log to Tracker</span>
                            </>
                          )}
                        </button>
                      ) : (
                        <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-xs flex items-center space-x-1 py-1 px-2.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Application Logged</span>
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Safe Metadata Recovery Provenance Banner */}
              {provenanceInfo && Object.keys(provenanceInfo).some((k) => provenanceInfo[k] !== 'tailored_resume') && (
                <div className="card-brutal bg-cream border-2 border-charcoal p-3 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>
                      <strong>Missing Metadata Safely Recovered:</strong>{' '}
                      {Object.keys(provenanceInfo)
                        .filter((k) => provenanceInfo[k] !== 'tailored_resume')
                        .map((k) => `${k.replace('contact.', '').replace(/\.\d+\./, ' ')} (from ${provenanceInfo[k].replace('_', ' ')})`)
                        .join(', ')}
                    </span>
                  </div>
                  <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600 text-[10px]">
                    Candidate Evidence Retained
                  </span>
                </div>
              )}

              {/* Main PDF Preview Window */}
              {pdfArtifact ? (
                <div className="card-brutal bg-white p-2 border-2 border-charcoal shadow-brutal space-y-2">
                  <div className="flex items-center justify-between px-3 py-1.5 border-b border-cream-border text-[11px] text-charcoal-muted">
                    <span className="flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span className="font-bold text-charcoal">
                        Resume PDF Preview
                      </span>
                    </span>
                    <span>
                      File Size:{" "}
                      {Math.round((pdfArtifact.file_size || 0) / 1024)} KB
                    </span>
                  </div>

                  {pdfPreviewUrl ? (
                    <PdfPreviewer
                      key={pdfRefreshKey}
                      pdfUrl={pdfPreviewUrl}
                      onRefresh={() => setPdfRefreshKey((key) => key + 1)}
                      title={pdfArtifact.file_name || "Compiled ATS PDF"}
                    />
                  ) : pdfPreviewLoading ? (
                    <div
                      role="status"
                      className="flex h-[780px] items-center justify-center border border-charcoal bg-white text-sm text-charcoal-muted"
                    >
                      Loading PDF preview...
                    </div>
                  ) : (
                    <div
                      role="alert"
                      className="flex h-[780px] flex-col items-center justify-center gap-3 border border-charcoal bg-white px-6 text-center text-sm text-charcoal-muted"
                    >
                      <p>{pdfPreviewError || "PDF preview is not available yet."}</p>
                      <button
                        type="button"
                        onClick={() => setPdfRefreshKey((key) => key + 1)}
                        className="btn-secondary"
                      >
                        Retry preview
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="card-brutal text-center py-16 space-y-4 bg-white border-2 border-charcoal">
                  <div className="w-12 h-12 rounded-full border-2 border-charcoal bg-cream-bg flex items-center justify-center mx-auto text-charcoal">
                    <FileCode className="w-6 h-6 text-coral" />
                  </div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-charcoal">
                    ATS Resume Not Yet Compiled
                  </h3>
                  <p className="text-xs text-charcoal-muted max-w-md mx-auto">
                    Click compile below to transform your tailored resume into
                    an ATS-parsable PDF document.
                  </p>
                  <button
                    onClick={handleGeneratePdf}
                    disabled={pdfLoading}
                    className="btn-primary inline-flex items-center space-x-2 text-xs py-2 px-4"
                  >
                    {pdfLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                        <span>Compiling LaTeX...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Compile ATS PDF</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Navigation CTAs */}
              <div className="flex justify-between items-center pt-4 border-t border-cream-border">
                <button
                  onClick={() => setCurrentStep(4)}
                  className="btn-secondary text-xs"
                >
                  â† Back to Stage 4: Resume Tailoring
                </button>
                <div className="text-xs text-charcoal-muted font-mono">
                  Stage 5: Final Resume Ready
                </div>
              </div>
            </div>
          )}
        </div>
      )}

