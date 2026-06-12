fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("../protos/AEGIS/health.proto").ok();
    Ok(())
}
