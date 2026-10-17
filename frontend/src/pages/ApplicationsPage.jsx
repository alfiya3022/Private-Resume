import React from 'react';
import { Briefcase, Calendar, CheckCircle2, ExternalLink } from 'lucide-react';

export default function ApplicationsPage() {
  const dummyApplications = [
    {
      id: 'app-1',
      company: 'Acme Systems',
      role: 'Full Stack Python/React Developer',
      status: 'Applied',
      matchScore: '88%',
      resumeVersion: 'Tailored-v2-acme.pdf',
      date: '2026-10-15',
    },
    {
      id: 'app-2',
      company: 'Nova AI Labs',
      role: 'Backend AI Engineer',
      status: 'Interview',
      matchScore: '92%',
      resumeVersion: 'Tailored-v1-nova.pdf',
      date: '2026-10-12',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="card-brutal">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-cream-border pb-4 mb-6">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-charcoal">
              Application Tracker
            </h2>
            <p className="text-sm text-charcoal-muted mt-1">
              Tracks submitted roles locked to exact, immutable historical resume snapshots.
            </p>
          </div>
          <button className="btn-primary">
            + New Application Record
          </button>
        </div>

        {/* Applications Table */}
        <div className="overflow-x-auto border-2 border-charcoal">
          <table className="w-full text-left text-sm">
            <thead className="bg-cream-muted border-b-2 border-charcoal text-xs font-mono uppercase text-charcoal">
              <tr>
                <th className="p-3">Company</th>
                <th className="p-3">Role</th>
                <th className="p-3">Status</th>
                <th className="p-3">Estimated Match</th>
                <th className="p-3">Resume Version</th>
                <th className="p-3">Applied Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cream-border bg-white">
              {dummyApplications.map((app) => (
                <tr key={app.id} className="hover:bg-cream transition-colors">
                  <td className="p-3 font-semibold text-charcoal">{app.company}</td>
                  <td className="p-3 text-charcoal-muted">{app.role}</td>
                  <td className="p-3">
                    <span className="badge-tag bg-emerald-50 text-emerald-800 border-emerald-600">
                      {app.status}
                    </span>
                  </td>
                  <td className="p-3 font-mono font-bold text-coral">{app.matchScore}</td>
                  <td className="p-3 font-mono text-xs text-charcoal flex items-center space-x-1">
                    <span>{app.resumeVersion}</span>
                    <ExternalLink className="w-3 h-3 text-charcoal-muted" />
                  </td>
                  <td className="p-3 font-mono text-xs text-charcoal-muted">{app.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
