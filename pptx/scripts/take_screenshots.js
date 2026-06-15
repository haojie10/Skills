const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCRATCH_DIR = 'C:/Users/066/.gemini/antigravity/brain/d160cf64-2927-4f09-808d-8f1c50f0a2a7/scratch';
const SLIDES_DIR = path.join(SCRATCH_DIR, 'slides');
const THUMB_OUT_DIR = path.join(SCRATCH_DIR, 'thumb_images');

if (!fs.existsSync(THUMB_OUT_DIR)) {
    fs.mkdirSync(THUMB_OUT_DIR, { recursive: true });
}

async function run() {
    console.log('启动 Chromium 浏览器...');
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    // 设为 960x540 (对应 720pt x 405pt 缩放)
    await page.setViewportSize({ width: 960, height: 540 });

    for (let i = 1; i <= 11; i++) {
        const slideName = `slide${String(i).padStart(2, '0')}.html`;
        const slidePath = path.join(SLIDES_DIR, slideName);
        if (!fs.existsSync(slidePath)) {
            console.error(`未找到 slide: ${slidePath}`);
            continue;
        }

        const fileUrl = `file:///${slidePath.replace(/\\/g, '/')}`;
        console.log(`正在渲染并截图: ${fileUrl}`);
        await page.goto(fileUrl);
        // 等待一些基本资源加载
        await page.waitForTimeout(500);

        const outPath = path.join(THUMB_OUT_DIR, `slide_${String(i).padStart(2, '0')}.png`);
        await page.screenshot({ path: outPath, type: 'png' });
        console.log(`截图已保存: ${outPath}`);
    }

    await browser.close();
    console.log('截图任务完成。');
}

run().catch(console.error);
