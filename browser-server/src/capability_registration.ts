/**
 * Capability Registration — registers Browser Server capabilities with AEGIS Core.
 *
 * On startup, the Browser Server connects to AEGIS Core and registers all
 * capabilities defined in safety.ts. The AEGIS Core's CapabilityRegistry
 * stores the metadata; actual execution is handled by the Browser Server's
 * gRPC service implementation.
 */

import type { BrowserServerConfig } from "./config.js";
import { BROWSER_CAPABILITIES } from "./safety.js";
import { logger } from "./logging.js";

/** Register all capabilities with the AEGIS Core. */
export async function registerCapabilities(config: BrowserServerConfig): Promise<void> {
  logger.info(`Registering ${BROWSER_CAPABILITIES.length} capabilities with AEGIS Core at ${config.aegisCoreAddress}`);

  for (const cap of BROWSER_CAPABILITIES) {
    // In production, this would call AEGIS Core's RegisterCapability gRPC endpoint.
    // For Phase 2.1, we log the registration as a placeholder.
    logger.info(`  Registered: ${cap.id} (${cap.name}) [${cap.safetyLevel}]`);
  }

  logger.info("Capability registration complete.");
}

/** Register a single capability (placeholder for gRPC call). */
export async function registerSingleCapability(
  _config: BrowserServerConfig,
  capability: typeof BROWSER_CAPABILITIES[number],
): Promise<void> {
  // TODO(Phase 2.x): Actual gRPC call to AEGIS Core
  // const client = getAegisCoreClient();
  // await client.RegisterCapability({ capability: { ... } });
  logger.debug(`Capability registered: ${capability.id}`);
}
