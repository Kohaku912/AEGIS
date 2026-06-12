//! gRPC Health Service for PC Server.
//!
//! Provides health check endpoint for Docker healthcheck and
//! AI Server connection verification.

use tonic::{Request, Response, Status, transport::Server};

// Inline health proto definitions to avoid build.rs complexity
pub mod health {
    tonic::include_proto!("aegis.health");
}

// Simple health check implementation
#[derive(Default)]
pub struct HealthService;

#[tonic::async_trait]
impl health::health_server::Health for HealthService {
    async fn check(
        &self,
        _request: Request<health::HealthCheckRequest>,
    ) -> Result<Response<health::HealthCheckResponse>, Status> {
        let reply = health::HealthCheckResponse {
            status: health::ServingStatus::Serving as i32,
            message: "ok".to_string(),
        };
        Ok(Response::new(reply))
    }
}

/// Start the gRPC server on the given address.
pub async fn start_grpc_server(addr: std::net::SocketAddr) -> Result<(), Box<dyn std::error::Error>> {
    let health_service = HealthService;
    println!("PC Server gRPC listening on {}", addr);

    Server::builder()
        .add_service(health::health_server::HealthServer::new(health_service))
        .serve(addr)
        .await?;

    Ok(())
}
