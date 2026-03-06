// 验证Marching Cubes查找表的脚本
const fs = require('fs');
const path = require('path');

// 读取查找表文件
const lookupTablePath = path.join(__dirname, 'src', 'components', 'MarchingCubesLookupTable.js');
const fileContent = fs.readFileSync(lookupTablePath, 'utf8');

// 提取triTable数组
const triTableMatch = fileContent.match(/export const triTable = \[(.*?)\]/s);
if (!triTableMatch) {
    console.error('无法找到triTable数组');
    process.exit(1);
}

const arrayContent = triTableMatch[1];

// 计算配置数量
const configCount = (arrayContent.match(/\[.*?\]/g) || []).length;

console.log('查找表配置数量:', configCount);
console.log('期望配置数量: 256');
console.log('配置数量是否正确:', configCount === 256);

// 检查数组格式
const lines = fileContent.split('\n');
let hasErrors = false;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.includes('// 配置') && line.includes(':')) {
        const configMatch = line.match(/配置(\d+):/);
        if (configMatch) {
            const configNumber = parseInt(configMatch[1]);
            // 检查下一行是否是数组
            if (i + 1 < lines.length && lines[i + 1].trim().startsWith('[')) {
                const arrayLine = lines[i + 1];
                // 检查数组是否以]结尾
                if (!arrayLine.trim().endsWith('],') && !arrayLine.trim().endsWith(']')) {
                    console.error(`配置${configNumber}的数组格式不正确: ${arrayLine}`);
                    hasErrors = true;
                }
            }
        }
    }
}

if (!hasErrors) {
    console.log('所有配置的数组格式正确');
}

// 检查最后一个配置是否为255
const lastConfigMatch = fileContent.match(/配置(\d+):.*?\n\s*\[.*?\]/g);
if (lastConfigMatch) {
    const lastConfig = lastConfigMatch[lastConfigMatch.length - 1];
    const lastConfigNumber = lastConfig.match(/配置(\d+):/)[1];
    console.log('最后一个配置编号:', lastConfigNumber);
    console.log('最后一个配置是否正确:', lastConfigNumber === '255');
}

console.log('验证完成');