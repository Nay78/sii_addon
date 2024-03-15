const puppetteer = require("puppeteer");
const path = require("path");
const xml2js = require("xml2js");
const fs = require("fs");
const process = require("process");
const util = require("util");

const args = process.argv.slice(2);
const RUT = args[0];
const PWD = args[1];

if (args.length < 2) {
  console.log("args", args);
  console.log("Please provide RUT and password");
  process.exit(1);
}

const URL1 = "https://www1.sii.cl/cgi-bin/Portal001/mipeLaunchPage.cgi?OPCION=1&TIPO=4";
const downloadPath = path.resolve("./downloads");
const userDataDir = path.resolve("./user_data");
if (!fs.existsSync(downloadPath)) {
  fs.mkdirSync(downloadPath);
}
if (!fs.existsSync(userDataDir)) {
  fs.mkdirSync(userDataDir);
}

const deleteFiles = async (directory) => {
  const files = await fs.promises.readdir(directory);
  for (const file of files) {
    await fs.promises.unlink(path.join(directory, file));
  }
};

const readFile = util.promisify(fs.readFile);

async function waitForFileAndReadContents(filePath) {
  return new Promise((resolve) => {
    const watcher = fs.watch(path.dirname(filePath), async (eventType, filename) => {
      if (filename === path.basename(filePath)) {
        fs.unwatchFile(filePath);
        watcher.close();
        const contents = await readFile(filePath, "utf8");
        resolve(contents);
      }
    });
  });
}

async function getDTE() {
  let result = { data: null, path: null };
  const browser = await puppetteer.launch({
    headless: false,
    userDataDir: "./user_data",
  });
  const page = await browser.newPage();
  const client = await page.createCDPSession();
  await client.send("Page.setDownloadBehavior", { behavior: "allow", downloadPath });

  await page.goto(URL1);

  // if page url contains InicioAutenticacion, then login
  if (page.url().includes("InicioAutenticacion")) {
    await (await page.$("#rutcntr")).type(RUT);
    await (await page.$("#clave")).type(PWD);
    await (await page.$("#bt_ingresar")).click();
  }

  // click download
  let lock = true;
  await page.setRequestInterception(true);
  page.on("request", async (request) => {
    request.continue();
  });

  page.on("response", async (response) => {
    const request = response.request();

    if (request.url().includes("DOWNLOAD=XML")) {
      const contenttype = response.headers()["content-type"];
      const filename = contenttype.split("filename=")[1];

      // check if filename is in download path:
      result["path"] = path.join(downloadPath, filename);
      result["data"] = await waitForFileAndReadContents(path.join(downloadPath, filename));
      // console.log(f); // OUTPUT
      lock = false;
    }
  });

  await page.waitForSelector("#my-wrapper > div.web-sii.cuerpo > div > p > input:nth-child(2)");
  const btn = await page.$("#my-wrapper > div.web-sii.cuerpo > div > p > input:nth-child(2)");
  await btn.click();

  while (lock) {
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  return result;
}

const parsex = async () => {
  fs.readdir(downloadPath, (err, files) => {
    if (err) throw err;

    let latestFile;
    let latestTime = 0;

    files.forEach((file) => {
      const filePath = path.join(downloadPath, file);
      const stat = fs.statSync(filePath);

      if (stat.mtimeMs > latestTime) {
        latestFile = filePath;
        latestTime = stat.mtimeMs;
      }
    });

    // Now, latestFile contains the path to the most recently modified file
    fs.readFile(latestFile, "utf8", (err, data) => {
      if (err) {
        console.error(err);

        return;
      }

      xml2js.parseString(data, (err, result) => {
        if (err) {
          console.error(err);
          return;
        }

        result;
      });
    });
  });
};

async function main() {
  // deleteFiles(downloadPath).catch(console.error);
  const dte = await getDTE();
  // if (dte.path.includes("DTE_DOWN")) {
  //   fs.unlink(dte.path, (err) => {
  //     if (err) {
  //       console.error(err);
  //       return;
  //     }
  //   });
  // }
  console.log(dte.data);
  if (dte.data) {
    process.exit(0);
  }
  process.exit(1);
}

main();
