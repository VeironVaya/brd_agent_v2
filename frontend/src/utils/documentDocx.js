import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx'

export async function downloadDocx(markdown, filename) {
  const children = []

  for (const raw of markdown.split('\n')) {
    const line = raw.trim()
    if (!line) {
      children.push(new Paragraph({ text: '' }))
      continue
    }
    
    if (line.startsWith('# ')) {
      children.push(new Paragraph({ text: line.slice(2), heading: HeadingLevel.HEADING_1 }))
    } else if (line.startsWith('## ')) {
      children.push(new Paragraph({ text: line.slice(3), heading: HeadingLevel.HEADING_2 }))
    } else if (line.startsWith('### ')) {
      children.push(new Paragraph({ text: line.slice(4), heading: HeadingLevel.HEADING_3 }))
    } else if (line.startsWith('**') && line.endsWith('**') && line.length > 3) {
      children.push(new Paragraph({ children: [new TextRun({ text: line.slice(2, -2), bold: true })] }))
    } else if (line.startsWith('_') && line.endsWith('_') && line.length > 1) {
      children.push(new Paragraph({ children: [new TextRun({ text: line.slice(1, -1), italics: true })] }))
    } else if (line.startsWith('*') && line.endsWith('*') && line.length > 1) {
      children.push(new Paragraph({ children: [new TextRun({ text: line.slice(1, -1), italics: true })] }))
    } else {
      children.push(new Paragraph({ text: line }))
    }
  }

  const doc = new Document({
    sections: [{ children }]
  })

  const blob = await Packer.toBlob(doc)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
