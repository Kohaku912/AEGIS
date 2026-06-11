/** Configuration for Browser Server. Loaded from environment variables. */

export interface BrowserServerConfig {
  port: number;
  host: string;
  aegisCoreAddress: string;
  browserType: "chromium" | "firefox" | "webkit";
  headless: boolean;
  logLevel: string;
}

export function loadConfig(): BrowserServerConfig {
  return {
    port: parseInt(process.env["AEGIS_BROWSER_GRPC_PORT"] || "50052", 10),
    host: process.env["AEGIS_BROWSER_HOST"] || "0.0.0.0",
    aegisCoreAddress: process.env["AEGIS_AI_GRPC_ADDR"] || "localhost:50051",
    browserType: (process.env["AEGIS_BROWSER_TYPE"] || "chromium") as BrowserServerConfig["browserType"],
    headless: process.env["AEGIS_BROWSER_HEADLESS"] !== "false",
    logLevel: process.env["AEGIS_LOG_LEVEL"] || "info",
  };
}
