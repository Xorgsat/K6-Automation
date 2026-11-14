export class RecommendationsPage {
  constructor(page) {
    this.page = page;
    this.heading = page.locator("h1");
    this.getPizzaButton = page.getByRole("button", { name: "Pizza, Please!" });
    this.recommendationsDiv = page.locator("div#recommendations");
    this.historySection = page.locator("div.history, div#history");
  }

  async goto(baseURL) {
    await this.page.goto(baseURL, { waitUntil: "networkidle" });
  }

  async getHeadingText() {
    return await this.heading.textContent();
  }

  async orderPizza() {
    await this.getPizzaButton.click();
    await this.page.waitForTimeout(600);
  }

  async getRecommendationText() {
    return await this.recommendationsDiv.textContent();
  }

  async takeScreenshot(path = "results/charts/browser_recommendation.png") {
    await this.page.screenshot({ path });
  }
}
