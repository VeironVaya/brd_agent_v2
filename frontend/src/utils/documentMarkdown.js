// Builds the Markdown representation of a BRD from its section tree +
// answers. This lives in the mock layer's conceptual "backend" boundary —
// per CLAUDE.md, once a real backend exists it would return this same
// markdown/text; only src/services/api.js's internals change. Client-side
// file-format conversion (Markdown -> PDF) is a separate, purely-frontend
// concern — see documentPdf.js.

import { SECTIONS, isLeaf, BOILERPLATE_SECTIONS } from './draftFields.js'
import { customChildrenFor, standaloneCustomSections } from './customSectionTree.js'

function appendLeaf(lines, leaf, answers) {
  const answer = answers[leaf.id]
  lines.push(`**${leaf.id} ${leaf.title}**`, '')
  lines.push(answer?.answer || '_Not yet answered._')
  lines.push('')
}

/** Recursive — arbitrary depth, so custom nodes use bold text rather than heading levels (markdown only goes to h6). */
function appendCustomNode(lines, node, code, answers) {
  lines.push(`**${code} ${node.title}**`, '')
  if (node.hasChildren) {
    node.children.forEach((child, i) => appendCustomNode(lines, child, `${code}.${i + 1}`, answers))
  } else {
    lines.push(answers[node.id]?.answer || '_Not yet answered._', '')
  }
}

export function buildMarkdown({ title, answers, customSections = [] }) {
  const lines = []
  const generatedOn = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  lines.push(`# ${title}`, '')
  lines.push(`*Business Requirement Document — Version 1.0 · Generated ${generatedOn}*`, '')

  for (const section of SECTIONS) {
    lines.push(`## ${section.id}. ${section.title}`, '')
    for (const node of section.children) {
      if (isLeaf(node)) {
        appendLeaf(lines, node, answers)
      } else {
        lines.push(`### ${node.id} ${node.title}`, '')
        for (const leaf of node.children) appendLeaf(lines, leaf, answers)
        for (const { node: cs, code } of customChildrenFor(customSections, node.id)) {
          appendCustomNode(lines, cs, code, answers)
        }
      }
    }
    for (const { node: cs, code } of customChildrenFor(customSections, section.id)) {
      appendCustomNode(lines, cs, code, answers)
    }
  }

  const boilerplate = BOILERPLATE_SECTIONS[0]
  lines.push(`## ${boilerplate.title}`, '')
  lines.push(boilerplate.description, '')

  const standalone = standaloneCustomSections(customSections)
  if (standalone.length) {
    lines.push('## Custom Sections', '')
    for (const { node, code } of standalone) {
      appendCustomNode(lines, node, code, answers)
    }
  }

  return lines.join('\n')
}
