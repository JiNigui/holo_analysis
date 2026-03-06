// 改进的Marching Cubes查找表验证脚本
const fs = require('fs');
const path = require('path');

// 读取查找表文件
const lookupTablePath = path.join(__dirname, 'src', 'components', 'MarchingCubesLookupTable.js');
const fileContent = fs.readFileSync(lookupTablePath, 'utf8');

// 统计配置数量
const configMatches = fileContent.match(/\/\/ 配置\d+:.*?\n\s*\[.*?\]/gs);
const configCount = configMatches ? configMatches.length : 0;

console.log('查找表配置数量:', configCount);
console.log('期望配置数量: 256');
console.log('配置数量是否正确:', configCount === 256);

// 检查配置编号的连续性
const configNumbers = [];
for (let i = 0; i < configCount; i++) {
    const match = configMatches[i].match(/配置(\d+):/);
    if (match) {
        configNumbers.push(parseInt(match[1]));
    }
}

// 检查编号是否连续
let isContinuous = true;
for (let i = 0; i < configNumbers.length; i++) {
    if (configNumbers[i] !== i) {
        console.error(`配置编号不连续: 期望${i}, 实际${configNumbers[i]}`);
        isContinuous = false;
        break;
    }
}

console.log('配置编号是否连续:', isContinuous);

// 检查数组格式
let hasFormatErrors = false;
for (let i = 0; i < configMatches.length; i++) {
    const configBlock = configMatches[i];
    const lines = configBlock.split('\n');
    
    // 检查数组行
    const arrayLine = lines.find(line => line.trim().startsWith('['));
    if (arrayLine) {
        const trimmedLine = arrayLine.trim();
        // 检查数组是否以],或]结尾
        if (!trimmedLine.endsWith('],') && !trimmedLine.endsWith(']')) {
            console.error(`配置${configNumbers[i]}的数组格式不正确: ${trimmedLine}`);
            hasFormatErrors = true;
        }
        
        // 检查数组内容是否包含-1
        if (!trimmedLine.includes('-1') && configNumbers[i] !== 255) {
            console.error(`配置${configNumbers[i]}可能缺少-1填充: ${trimmedLine}`);
            hasFormatErrors = true;
        }
    }
}

if (!hasFormatErrors) {
    console.log('所有配置的数组格式正确');
}

// 检查特殊配置
console.log('\\n特殊配置检查:');
console.log('配置0 (无顶点激活):', configMatches[0].includes('[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]'));
console.log('配置255 (所有顶点激活):', configMatches[255].includes('[0, 8, 3, 0, 1, 9, 1, 2, 10, 2, 3, 11, 4, 7, 8, 4, 5, 9, 5, 6, 10, 6, 7, 11]'));

console.log('\\n验证完成');