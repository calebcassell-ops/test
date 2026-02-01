import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';
import * as cheerio from 'cheerio';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.join(__dirname, '..');
const VERSIONS_DIR = path.join(ROOT_DIR, 'versions');
const CHANGELOG_FILE = path.join(ROOT_DIR, 'CHANGELOG.md');
const LATEST_FILE = path.join(VERSIONS_DIR, 'latest.txt');
const METADATA_FILE = path.join(VERSIONS_DIR, 'metadata.json');

const CONSTITUTION_URL = 'https://www.anthropic.com/constitution';

/**
 * Fetch the constitution page and extract text content
 */
export async function fetchConstitution() {
  console.log(`Fetching ${CONSTITUTION_URL}...`);

  const response = await fetch(CONSTITUTION_URL, {
    headers: {
      'User-Agent': 'ConstitutionMonitor/1.0'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
  }

  const html = await response.text();
  return extractContent(html);
}

/**
 * Extract text content from HTML with proper spacing between elements
 */
function extractContent(html) {
  const $ = cheerio.load(html);

  // Remove non-content elements
  $('script, style, nav, header, footer, noscript, iframe').remove();

  // Get main content
  const mainContent = $('article').length ? $('article') : ($('main').length ? $('main') : $('body'));

  // Block-level elements that should have newlines before/after
  const blockElements = new Set([
    'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'ul', 'ol', 'blockquote', 'section', 'article',
    'tr', 'td', 'th', 'br', 'hr'
  ]);

  // Extract text with proper spacing between block elements
  const textParts = [];

  function extractFromNode(node) {
    if (node.type === 'text') {
      const text = node.data.trim();
      if (text) {
        textParts.push(text);
      }
    } else if (node.type === 'tag') {
      const tagName = node.name.toLowerCase();
      const isBlock = blockElements.has(tagName);

      // Add newline marker before block elements
      if (isBlock && textParts.length > 0) {
        textParts.push('\n');
      }

      // Process children
      if (node.children) {
        for (const child of node.children) {
          extractFromNode(child);
        }
      }

      // Add newline marker after block elements
      if (isBlock) {
        textParts.push('\n');
      }
    }
  }

  // Process all nodes in main content
  mainContent.contents().each(function() {
    extractFromNode(this);
  });

  // Join and normalize whitespace
  let text = textParts.join(' ');

  // Normalize multiple spaces to single space
  text = text.replace(/[ \t]+/g, ' ');

  // Normalize multiple newlines to double newline (paragraph break)
  text = text.replace(/\n\s*\n/g, '\n\n');
  text = text.replace(/\n{3,}/g, '\n\n');

  // Split into lines and clean up
  const lines = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  return lines.join('\n');
}

/**
 * Generate a short hash of content
 */
export function getContentHash(content) {
  return crypto.createHash('sha256').update(content).digest('hex').slice(0, 12);
}

/**
 * Load metadata about stored versions
 */
export async function loadMetadata() {
  try {
    const data = await fs.readFile(METADATA_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { versions: [] };
  }
}

/**
 * Save metadata
 */
async function saveMetadata(metadata) {
  await fs.writeFile(METADATA_FILE, JSON.stringify(metadata, null, 2));
}

/**
 * Update the last checked timestamp
 */
async function updateLastChecked() {
  const metadata = await loadMetadata();
  metadata.lastChecked = new Date().toISOString();
  await saveMetadata(metadata);
}

/**
 * Get the last checked timestamp
 */
export async function getLastChecked() {
  const metadata = await loadMetadata();
  return metadata.lastChecked || null;
}

/**
 * Get the latest stored version
 */
export async function getLatestVersion() {
  try {
    return await fs.readFile(LATEST_FILE, 'utf-8');
  } catch {
    return null;
  }
}

/**
 * Generate a unified diff between old and new content
 */
export function generateDiff(oldContent, newContent) {
  const oldLines = oldContent.split('\n');
  const newLines = newContent.split('\n');

  const diff = [];
  diff.push('--- previous');
  diff.push('+++ current');

  // Simple line-by-line diff
  const maxLen = Math.max(oldLines.length, newLines.length);
  let contextStart = -1;
  let changes = [];

  for (let i = 0; i < maxLen; i++) {
    const oldLine = oldLines[i] || '';
    const newLine = newLines[i] || '';

    if (oldLine !== newLine) {
      if (oldLine) changes.push(`- ${oldLine}`);
      if (newLine) changes.push(`+ ${newLine}`);
    }
  }

  return [...diff, ...changes].join('\n');
}

/**
 * Split text into sentences
 */
function splitIntoSentences(text) {
  // Split on sentence-ending punctuation followed by space or newline
  // Keep the punctuation with the sentence
  return text
    .replace(/\n+/g, ' ')  // Normalize newlines to spaces
    .replace(/\s+/g, ' ')  // Normalize whitespace
    .split(/(?<=[.!?])\s+/)
    .map(s => s.trim())
    .filter(s => s.length > 10);  // Filter out very short fragments
}

/**
 * Generate summary statistics of changes (by sentence, deduplicated)
 */
export function generateDiffSummary(oldContent, newContent) {
  const oldSentences = splitIntoSentences(oldContent);
  const newSentences = splitIntoSentences(newContent);

  const oldSet = new Set(oldSentences);
  const newSet = new Set(newSentences);

  // Find unique additions (in new but not old)
  const addedSet = new Set();
  const added = [];
  for (const s of newSentences) {
    if (!oldSet.has(s) && !addedSet.has(s)) {
      addedSet.add(s);
      added.push(s);
    }
  }

  // Find unique removals (in old but not new)
  const removedSet = new Set();
  const removed = [];
  for (const s of oldSentences) {
    if (!newSet.has(s) && !removedSet.has(s)) {
      removedSet.add(s);
      removed.push(s);
    }
  }

  return {
    linesAdded: added.length,
    linesRemoved: removed.length,
    added,
    removed
  };
}

/**
 * Generate LLM summary using Claude API
 */
async function generateLLMSummary(oldContent, newContent, diff) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.log('No ANTHROPIC_API_KEY found, skipping LLM summary');
    return null;
  }

  console.log('Generating LLM summary...');

  const prompt = `Analyze the following diff of Anthropic's AI constitution and provide a brief,
human-readable summary of what changed. Focus on the substantive changes to principles,
guidelines, or policies. Be concise (2-4 sentences).

DIFF:
${diff.slice(0, 8000)}

Provide only the summary, no preamble.`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 500,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    return result.content[0].text;
  } catch (error) {
    console.error('Error generating LLM summary:', error.message);
    return null;
  }
}

/**
 * Update the changelog file
 */
async function updateChangelog(timestamp, versionHash, diffSummary, llmSummary) {
  let entry = `
## ${timestamp}

**Version:** [\`${versionHash}\`](https://www.anthropic.com/constitution)

`;

  if (llmSummary) {
    entry += `### Summary\n${llmSummary}\n\n`;
  }

  entry += `**Changes:** +${diffSummary.linesAdded} additions, -${diffSummary.linesRemoved} removals\n\n`;

  if (diffSummary.added.length > 0) {
    entry += '<details>\n<summary>Additions</summary>\n\n';
    for (const line of diffSummary.added) {
      if (line.trim()) {
        entry += `> ${line}\n\n`;
      }
    }
    entry += '</details>\n\n';
  }

  if (diffSummary.removed.length > 0) {
    entry += '<details>\n<summary>Removals</summary>\n\n';
    for (const line of diffSummary.removed) {
      if (line.trim()) {
        entry += `> ~~${line}~~\n\n`;
      }
    }
    entry += '</details>\n\n';
  }

  entry += '---\n';

  // Read existing changelog
  let existing = '';
  try {
    existing = await fs.readFile(CHANGELOG_FILE, 'utf-8');
  } catch {
    // File doesn't exist, create header
  }

  let newContent;
  if (existing && existing.includes('---')) {
    const parts = existing.split('---');
    const header = parts[0] + '---\n';
    const rest = parts.slice(1).join('---');
    newContent = header + entry + rest;
  } else {
    const header = `# Anthropic Constitution Changelog

This file tracks all detected changes to [Anthropic's Constitution](https://www.anthropic.com/constitution).

Each entry includes:
- Timestamp of when the change was detected
- A summary of what changed
- Statistics on additions/removals

---
`;
    newContent = header + entry;
  }

  await fs.writeFile(CHANGELOG_FILE, newContent);
  console.log(`Updated ${CHANGELOG_FILE}`);
}

/**
 * Save a new version
 */
async function saveVersion(content, timestamp, versionHash) {
  await fs.mkdir(VERSIONS_DIR, { recursive: true });

  // Save as latest
  await fs.writeFile(LATEST_FILE, content);

  // Save timestamped version
  const safeTimestamp = timestamp.replace(/:/g, '-').replace(/ /g, '_');
  const versionFile = path.join(VERSIONS_DIR, `${safeTimestamp}_${versionHash}.txt`);
  await fs.writeFile(versionFile, content);

  // Update metadata
  const metadata = await loadMetadata();
  metadata.versions.push({
    timestamp,
    hash: versionHash,
    file: path.basename(versionFile)
  });
  await saveMetadata(metadata);

  console.log(`Saved new version: ${path.basename(versionFile)}`);
}

/**
 * Main monitoring function
 */
export async function runMonitor() {
  console.log('='.repeat(60));
  console.log('Constitution Monitor');
  console.log('='.repeat(60));

  await fs.mkdir(VERSIONS_DIR, { recursive: true });

  // Update last checked timestamp
  await updateLastChecked();

  // Fetch current content
  const currentContent = await fetchConstitution();
  const currentHash = getContentHash(currentContent);
  const timestamp = new Date().toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC');

  console.log(`Fetched content, hash: ${currentHash}`);
  console.log(`Timestamp: ${timestamp}`);

  // Get previous version
  const previousContent = await getLatestVersion();

  if (!previousContent) {
    console.log('\nFirst run - saving initial version');
    await saveVersion(currentContent, timestamp, currentHash);

    // Create initial changelog
    const initialChangelog = `# Anthropic Constitution Changelog

This file tracks all detected changes to [Anthropic's Constitution](https://www.anthropic.com/constitution).

Each entry includes:
- Timestamp of when the change was detected
- A summary of what changed
- Statistics on additions/removals

---

## ${timestamp} (Initial)

**Version:** \`${currentHash}\`

Initial snapshot captured. Future changes will be logged here.

---
`;
    await fs.writeFile(CHANGELOG_FILE, initialChangelog);

    return { changed: false, initial: true, hash: currentHash };
  }

  const previousHash = getContentHash(previousContent);

  if (currentHash === previousHash) {
    console.log('\nNo changes detected.');
    return { changed: false, hash: currentHash };
  }

  // Changes detected!
  console.log('\n' + '!'.repeat(60));
  console.log('CHANGES DETECTED!');
  console.log('!'.repeat(60));

  // Generate diff
  const diff = generateDiff(previousContent, currentContent);
  const diffSummary = generateDiffSummary(previousContent, currentContent);

  console.log(`\nChanges: +${diffSummary.linesAdded} / -${diffSummary.linesRemoved} lines`);

  // Save diff file
  const safeTimestamp = timestamp.replace(/:/g, '-').replace(/ /g, '_');
  const diffFile = path.join(VERSIONS_DIR, `${safeTimestamp}_${currentHash}.diff`);
  await fs.writeFile(diffFile, diff);
  console.log(`Saved diff: ${path.basename(diffFile)}`);

  // Generate LLM summary
  const llmSummary = await generateLLMSummary(previousContent, currentContent, diff);
  if (llmSummary) {
    console.log(`\nLLM Summary: ${llmSummary}`);
  }

  // Save new version
  await saveVersion(currentContent, timestamp, currentHash);

  // Update changelog
  await updateChangelog(timestamp, currentHash, diffSummary, llmSummary);

  console.log('\nDone! Check CHANGELOG.md for details.');

  return {
    changed: true,
    hash: currentHash,
    summary: llmSummary || `Changes detected: +${diffSummary.linesAdded}/-${diffSummary.linesRemoved} lines`,
    diffSummary
  };
}

/**
 * Get changelog content
 */
export async function getChangelog() {
  try {
    return await fs.readFile(CHANGELOG_FILE, 'utf-8');
  } catch {
    return '# No changelog yet\n\nRun the monitor to capture the first snapshot.';
  }
}

/**
 * Get all versions metadata
 */
export async function getVersions() {
  const metadata = await loadMetadata();
  return metadata.versions;
}

/**
 * Get a specific version's content
 */
export async function getVersion(hash) {
  const metadata = await loadMetadata();
  const version = metadata.versions.find(v => v.hash === hash);

  if (!version) return null;

  const filePath = path.join(VERSIONS_DIR, version.file);
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return { ...version, content };
  } catch {
    return null;
  }
}
