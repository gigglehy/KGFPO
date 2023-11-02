/**
 * 爬取国家减灾网的灾害事件数据
 * */

const puppeteer = require('puppeteer');
const ObjectsToCsv = require('objects-to-csv');
const XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;
const csv2json = require('csvtojson')


// 爬取文章列表，并存储为csv
const record_links = async (page) => {
    // 选择文章列表元素 body > section > div.main-show.main-overview > div > ul
    let rec_all_list = [];
    while (true) {
        await page.waitForSelector('li.laws-item');
        let rec_sublist = await page.evaluate((selector) => {
            let lis = document.querySelectorAll(selector);
            let rec_list = []
            lis.forEach(li => {
                let title = li.children[0].innerText;
                let link = li.children[0].href;
                let datetime = li.children[1].innerText;
                rec_list.push({
                    title: title,
                    link: link,
                    publishTime: datetime
                });
            })
            return rec_list;
        }, 'li.laws-item')
        rec_all_list = rec_all_list.concat(rec_sublist);

        if (await page.$('.next')) {

            await page.waitFor(1000);
            await page.click('.next');
        } else {
            console.log(await page.$('.next'));
            break;
        }
    }
    console.log(rec_all_list.length)
    var file = "./article_list.csv"
    new ObjectsToCsv(rec_all_list).toDisk(file, { allColumns: true, append: true });
    return rec_all_list;
}

// 读取csv文件
function csv2Json(csv) {
    const lines = csv.split("\n");
    const result = [];
    const headers = lines[0].split(",");
    for (let i = 1; i < lines.length; i++) {
        const obj = {};
        const currentLine = lines[i].split(",");
        for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentLine[j];
        }
        result.push(obj);
    }
    return result;
}

// 爬取文章的内容
const record_article = async (page) => {
    let article_content = "";
    await page.waitForSelector("div.rich-text");
    article_content = await page.evaluate((selector) => {
        return document.querySelector("div.rich-text").innerHTML.replace(/[ ]|[\r\n]|<[^<>]+>/g, "")
    }, "div.rich-text")
    // console.log(article_content);
    return article_content;
}

// 主函数
(async () => {
    // 打开浏览器，爬取文章列表
    const browser = await puppeteer.launch({
        headless: false,
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    });
    let page = await browser.newPage();
    console.log("ready to go to the page")
    await page.goto('http://www.ndrcc.org.cn/zxzq/index.jhtml', {
        waitUntil: 'domcontentloaded' // Remove the timeout
        ,
        timeout: 0
    });
    console.log("go to the page")
    await page.setRequestInterception(true);
    page.on('request', async req => {
        if (req.url().match(/analyse.weather.com.cn/g)) {
            req.abort();
        } else {
            await req.continue();
        }
    })
    await page.close();

    //打开新的标签页，用于爬取文章内容

    let article_list = [];
    await csv2json()        // 加了await可以先让promise的函数运行完之后在执行后面的逻辑
        .fromFile('./article_list.csv') ///只能读取utf-8编码，如果不是，需要转一下
        .then((json) => {
            article_list = json;
        })

    for (let i = 0; i < article_list.length; i++) {
        console.log("reading the article No." + i.toString())
        let link = article_list[i].link;
        //打开新的标签页，用于爬取文章内容
        page = await browser.newPage();
        await page.goto(link, {
            waitUntil: 'domcontentloaded',
            timeout: 0
        })
        let content = await record_article(page);
        article_list[i].content = content;

        // 爬完关闭
        await page.close();

    }
    var _file = "./article_content.csv"
    new ObjectsToCsv(article_list).toDisk(_file, { allColumns: true, append: true });
    // page = await browser.newPage();


    await browser.close();
})();