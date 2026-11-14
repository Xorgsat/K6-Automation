import { browser } from "k6/browser";
import { check, sleep } from "k6";
import { RecommendationsPage } from "./pages/recommendations-page.js";
import { LoginPage } from "./pages/login-page.js";

const BASE_URL = __ENV.BASE_URL || "http://localhost:3333";

export const options = {
  scenarios: {
    customer_journey: {
      executor: "shared-iterations",
      vus: 1,
      iterations: 2,
      maxDuration: "1m",
      options: {
        browser: {
          type: "chromium",
        },
      },
      exec: "customerJourney",
    },
    admin_journey: {
      executor: "shared-iterations",
      vus: 1,
      iterations: 1,
      maxDuration: "1m",
      startTime: "5s",
      options: {
        browser: {
          type: "chromium",
        },
      },
      exec: "adminJourney",
    },
  },
  thresholds: {
    browser_http_req_failed: ["rate<0.01"],
    browser_web_vital_fcp: ["p(95)<3000"],
    browser_web_vital_lcp: ["p(95)<4000"],
  },
};

export async function customerJourney() {
  const page = await browser.newPage();
  try {
    const recPage = new RecommendationsPage(page);
    await recPage.goto(BASE_URL);

    const heading = await recPage.getHeadingText();
    check(heading, {
      "homepage heading loaded": (h) => h && h.includes("Looking to break out of your pizza routine?"),
    });

    // Request pizza recommendation
    await recPage.orderPizza();
    const recText = await recPage.getRecommendationText();
    check(recText, {
      "recommendation generated": (t) => t && t.length > 5,
    });

    await recPage.takeScreenshot("results/charts/browser_customer_journey.png");
    sleep(1);
  } finally {
    await page.close();
  }
}

export async function adminJourney() {
  const page = await browser.newPage();
  try {
    const loginPage = new LoginPage(page);
    await loginPage.goto(BASE_URL);
    await loginPage.login();

    const logoutText = await loginPage.getLogoutButtonText();
    check(logoutText, {
      "admin login successful": (text) => text === "Logout",
    });

    await loginPage.takeScreenshot("results/charts/browser_admin_journey.png");
    sleep(1);
  } finally {
    await page.close();
  }
}
