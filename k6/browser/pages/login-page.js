export class LoginPage {
  constructor(page) {
    this.page = page;
    this.signInButton = page.getByRole("button", { name: "Sign in" });
    this.logoutButton = page.getByRole("button", { name: "Logout" });
  }

  async goto(baseURL) {
    await this.page.goto(`${baseURL}/admin`, { waitUntil: "networkidle" });
  }

  async login() {
    await this.signInButton.click();
    await this.page.waitForTimeout(500);
  }

  async getLogoutButtonText() {
    return await this.logoutButton.textContent();
  }

  async takeScreenshot(path = "results/charts/browser_admin_login.png") {
    await this.page.screenshot({ path });
  }
}
