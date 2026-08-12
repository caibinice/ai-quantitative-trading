import fs from 'node:fs'
import path from 'node:path'
import JavaScriptObfuscator from 'javascript-obfuscator'

const assets = path.resolve('dist/assets')
if (!fs.existsSync(assets)) process.exit(0)

const obfuscated = []
const skippedVendors = []
for (const name of fs.readdirSync(assets)) {
  if (!name.endsWith('.js')) continue
  if (name.startsWith('vendor-') || name.startsWith('rolldown-runtime')) {
    skippedVendors.push(name)
    continue
  }
  const file = path.join(assets, name)
  const source = fs.readFileSync(file, 'utf8')
  const result = JavaScriptObfuscator.obfuscate(source, {
    compact: true,
    controlFlowFlattening: false,
    deadCodeInjection: false,
    debugProtection: false,
    identifierNamesGenerator: 'hexadecimal',
    renameGlobals: false,
    renameProperties: false,
    selfDefending: false,
    simplify: true,
    splitStrings: false,
    stringArray: true,
    stringArrayEncoding: [],
    stringArrayThreshold: 0.35,
    target: 'browser',
    transformObjectKeys: false,
  })
  fs.writeFileSync(file, result.getObfuscatedCode())
  obfuscated.push(name)
  process.stdout.write(`Obfuscated ${name}\n`)
}

fs.mkdirSync(path.resolve('../.deploy'), { recursive: true })
fs.writeFileSync(
  path.resolve('../.deploy/obfuscation-report.json'),
  `${JSON.stringify({ obfuscated, skippedVendors, sourceMaps: false }, null, 2)}\n`,
)
