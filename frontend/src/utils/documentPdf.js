// Client-side file generation for the Export flow. The mock "backend"
// (src/services/api.js) only ever hands back markdown/text — converting
// that into an actual downloadable .md or .pdf file is frontend work, so it
// lives here rather than being simulated as a server capability.

import { jsPDF } from 'jspdf'

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export function downloadMarkdown(markdown, filename) {
  downloadBlob(new Blob([markdown], { type: 'text/markdown' }), filename)
}

/** Minimal markdown -> PDF renderer: enough heading/paragraph/emphasis support for a BRD document. */
function markdownToPdfBlob(markdown) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const marginX = 56
  const marginTop = 64
  const marginBottom = 64
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const maxWidth = pageWidth - marginX * 2
  let y = marginTop

  function ensureSpace(lineHeight) {
    if (y + lineHeight > pageHeight - marginBottom) {
      doc.addPage()
      y = marginTop
    }
  }

  function paragraph(text, { font = 'normal', size = 10.5, lineHeight = 14, gapAfter = 6 } = {}) {
    doc.setFont('helvetica', font)
    doc.setFontSize(size)
    const wrapped = doc.splitTextToSize(text, maxWidth)
    for (const line of wrapped) {
      ensureSpace(lineHeight)
      doc.text(line, marginX, y)
      y += lineHeight
    }
    y += gapAfter
  }

  for (const raw of markdown.split('\n')) {
    const line = raw.trim()
    if (!line) {
      y += 6
      continue
    }
    if (line.startsWith('# ')) {
      paragraph(line.slice(2), { font: 'bold', size: 20, lineHeight: 24, gapAfter: 10 })
    } else if (line.startsWith('## ')) {
      paragraph(line.slice(3), { font: 'bold', size: 14, lineHeight: 18, gapAfter: 8 })
    } else if (line.startsWith('### ')) {
      paragraph(line.slice(4), { font: 'bold', size: 11.5, lineHeight: 15, gapAfter: 6 })
    } else if (line.startsWith('**') && line.endsWith('**') && line.length > 3) {
      paragraph(line.slice(2, -2), { font: 'bold', size: 10.5, lineHeight: 14, gapAfter: 3 })
    } else if (line.startsWith('_') && line.endsWith('_') && line.length > 1) {
      paragraph(line.slice(1, -1), { font: 'italic', size: 9.5, lineHeight: 13, gapAfter: 6 })
    } else if (line.startsWith('*') && line.endsWith('*') && line.length > 1) {
      paragraph(line.slice(1, -1), { font: 'italic', size: 9.5, lineHeight: 13, gapAfter: 6 })
    } else {
      paragraph(line, { gapAfter: 6 })
    }
  }

  return doc.output('blob')
}

export function downloadPdf(markdown, filename) {
  downloadBlob(markdownToPdfBlob(markdown), filename)
}
