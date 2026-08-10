// Recursive helpers for arbitrary-depth CustomSections. This is prototype
// logic — a real backend would own numbering/validation and just hand the
// frontend the resolved tree + codes; this mock does the same computation
// client-side so the UI has something real to render against.

import { SECTIONS, isLeaf } from './draftFields.js'

function templateNode(nodeId) {
  for (const top of SECTIONS) {
    if (top.id === nodeId) return top
    for (const child of top.children) {
      if (!isLeaf(child) && child.id === nodeId) return child
    }
  }
  return null
}

function templateChildCount(nestUnder) {
  if (!nestUnder) return SECTIONS.length
  const node = templateNode(nestUnder)
  return node ? node.children.length : 0
}

/** Computed dotted code for a top-level custom section at `index` in the array. */
export function topLevelCode(customSections, index) {
  const node = customSections[index]
  const siblingsBefore = customSections
    .slice(0, index)
    .filter((cs) => cs.nestUnder === node.nestUnder).length
  const position = templateChildCount(node.nestUnder) + siblingsBefore + 1
  return node.nestUnder ? `${node.nestUnder}.${position}` : `${position}`
}

/** Computed dotted code for a nested child at `index` within its parent's children array. */
export function childCode(parentCode, index) {
  return `${parentCode}.${index + 1}`
}

function codeInChildren(children, parentCode, id) {
  for (let i = 0; i < children.length; i++) {
    const code = childCode(parentCode, i)
    if (children[i].id === id) return code
    const found = codeInChildren(children[i].children, code, id)
    if (found) return found
  }
  return null
}

/** Computed display code for a custom node anywhere in the tree, by id (or null if not found). */
export function getCodeForNode(customSections, id) {
  for (let i = 0; i < customSections.length; i++) {
    const node = customSections[i]
    const code = topLevelCode(customSections, i)
    if (node.id === id) return code
    const found = codeInChildren(node.children, code, id)
    if (found) return found
  }
  return null
}

/** Top-level custom sections nested under a given template node id, each with its computed code. */
export function customChildrenFor(customSections, parentId) {
  return customSections
    .map((node, i) => ({ node, index: i }))
    .filter(({ node }) => node.nestUnder === parentId)
    .map(({ node, index }) => ({ node, code: topLevelCode(customSections, index) }))
}

/** Standalone (nestUnder: null) top-level custom sections, each with its computed code. */
export function standaloneCustomSections(customSections) {
  return customSections
    .map((node, i) => ({ node, index: i }))
    .filter(({ node }) => !node.nestUnder)
    .map(({ node, index }) => ({ node, code: topLevelCode(customSections, index) }))
}

/** Find a node anywhere in the (possibly nested) custom section tree by id. */
export function findCustomNode(customSections, id) {
  for (const node of customSections) {
    if (node.id === id) return node
    const found = findCustomNode(node.children, id)
    if (found) return found
  }
  return null
}

/**
 * Return a new tree with the node matching `id` replaced by `fn(node)`,
 * or removed entirely if `fn` returns null (used for rename/remove).
 */
export function mutateCustomTree(customSections, id, fn) {
  return customSections
    .map((node) => (node.id === id ? fn(node) : { ...node, children: mutateCustomTree(node.children, id, fn) }))
    .filter((node) => node !== null)
}

/** Append `newNode` as a child of the node matching `parentId`, anywhere in the tree. */
export function addChildToNode(customSections, parentId, newNode) {
  return customSections.map((node) =>
    node.id === parentId
      ? { ...node, children: [...node.children, newNode] }
      : { ...node, children: addChildToNode(node.children, parentId, newNode) },
  )
}

/**
 * Live-scanned list of every valid "nest under" target: template headers
 * (never leaves) plus existing custom groups (hasChildren: true), at any
 * depth, each with its current computed code. Re-run this every time the
 * "Add Custom Section" modal opens so newly-added deep nodes are pickable
 * immediately.
 */
export function getContainerOptions(customSections) {
  const options = [{ id: null, kind: 'standalone', label: 'None — standalone top-level section', depth: 0 }]

  function walkTemplate(nodes, depth) {
    for (const node of nodes) {
      if (!isLeaf(node)) {
        options.push({ id: node.id, kind: 'template', label: `${node.id} ${node.title}`, depth })
        walkTemplate(node.children, depth + 1)
      }
    }
  }
  for (const top of SECTIONS) {
    options.push({ id: top.id, kind: 'template', label: `${top.id}. ${top.title}`, depth: 0 })
    walkTemplate(top.children, 1)
  }

  function walkCustom(nodes, parentCode, depth) {
    nodes.forEach((node, i) => {
      if (!node.hasChildren) return
      const code = childCode(parentCode, i)
      options.push({ id: node.id, kind: 'custom', label: `${code} ${node.title}`, depth })
      walkCustom(node.children, code, depth + 1)
    })
  }
  const customTopLevel = customSections.filter((n) => n.hasChildren)
  if (customTopLevel.length > 0) {
    options.push({ id: '__custom_divider__', kind: 'divider', label: 'Existing custom sections', depth: 0 })
    customSections.forEach((node, i) => {
      if (!node.hasChildren) return
      const code = topLevelCode(customSections, i)
      options.push({ id: node.id, kind: 'custom', label: `${code} ${node.title}`, depth: 0 })
      walkCustom(node.children, code, 1)
    })
  }

  return options
}
