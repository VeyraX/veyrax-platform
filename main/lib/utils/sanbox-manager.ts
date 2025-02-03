import { Sandbox } from '@e2b/code-interpreter';

class SandboxManager {
  private static instance: SandboxManager;
  private activeSandbox: { id: string; lastUsed: Date } | null = null;
  private readonly SANDBOX_TIMEOUT = 30 * 60 * 1000;

  private constructor() {}

  static getInstance(): SandboxManager {
    if (!SandboxManager.instance) {
      SandboxManager.instance = new SandboxManager();
    }
    return SandboxManager.instance;
  }

  getCurrentSandboxId(): string | null {
    return this.activeSandbox?.id || null;
  }

  setCurrentSandbox(sandboxId: string) {
    this.activeSandbox = {
      id: sandboxId,
      lastUsed: new Date()
    };
  }

  async getSandbox(): Promise<Sandbox> {
    if (this.activeSandbox) {
      const timeSinceLastUse = Date.now() - this.activeSandbox.lastUsed.getTime();
      
      if (timeSinceLastUse < this.SANDBOX_TIMEOUT) {
        try {
          const runningSandboxes = await Sandbox.list();
          const existingSandbox = runningSandboxes.find(
            sandbox => sandbox.sandboxId === this.activeSandbox?.id
          );
          
          if (existingSandbox) {
            const sandbox = await Sandbox.connect(this.activeSandbox.id);
            this.activeSandbox.lastUsed = new Date();
            return sandbox;
          }
          this.activeSandbox = null;
        } catch (error) {
          this.activeSandbox = null;
        }
      } else {
        this.activeSandbox = null;
      }
    }

    const sandbox = await Sandbox.create();
    this.activeSandbox = {
      id: sandbox.sandboxId,
      lastUsed: new Date()
    };
    return sandbox;
  }
}

export const sandboxManager = SandboxManager.getInstance();