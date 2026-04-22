#!/usr/bin/env node
/**
 * 将 Markdown 中的本地图片引用替换为 jsDelivr CDN URL
 * 用法：node scripts/img-to-cdn.js [file.md]
 *       不传参数则扫描所有 content/ 下的 .md 文件
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

const CDN_BASE = 'https://cdn.jsdelivr.net/gh/skyseraph/skyseraph.github.io@main/static'
const LOCAL_IMG_RE = /!\[([^\]]*)\]\((\/images\/[^)]+)\)/g

function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8')
  let changed = false
  const updated = content.replace(LOCAL_IMG_RE, (match, alt, imgPath) => {
    changed = true
    return `![${alt}](${CDN_BASE}${imgPath})`
  })
  if (changed) {
    fs.writeFileSync(filePath, updated, 'utf8')
    console.log(`✓ ${filePath}`)
  }
}

function findMdFiles(dir) {
  const results = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) results.push(...findMdFiles(full))
    else if (entry.name.endsWith('.md')) results.push(full)
  }
  return results
}

const root = path.resolve(__dirname, '..')
const targets = process.argv[2]
  ? [path.resolve(process.argv[2])]
  : findMdFiles(path.join(root, 'content'))

targets.forEach(processFile)
console.log(`\ndone — ${targets.length} file(s) scanned`)
