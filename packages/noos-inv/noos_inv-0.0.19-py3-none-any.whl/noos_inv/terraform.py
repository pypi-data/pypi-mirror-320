from invoke import Collection, Context, task


CONFIG = {
    "terraform": {
        "organisation": None,
        "workspace": None,
        "token": None,
    }
}


# Terraform deployment workflow


@task()
def update(
    ctx: Context,
    variable: str = "",
    value: str = "",
    organisation: str | None = None,
    workspace: str | None = None,
    token: str | None = None,
) -> None:
    """Update variable in Terraform cloud."""
    cmd = f"noostf update --variable {variable} --value '{value}'"
    ctx.run(cmd + _append_credentials(ctx, organisation, workspace, token), pty=True)


@task()
def run(
    ctx,
    message: str = "",
    organisation: str | None = None,
    workspace: str | None = None,
    token: str | None = None,
) -> None:
    """Run a plan in Terraform cloud."""
    cmd = f"noostf run --message '{message}'"
    ctx.run(cmd + _append_credentials(ctx, organisation, workspace, token), pty=True)


def _append_credentials(
    ctx: Context, organisation: str | None, workspace: str | None, token: str | None
) -> str:
    cmd = ""
    for arg in ctx.terraform:
        # Check credentials
        secret = locals()[arg] or ctx.terraform[arg]
        assert secret is not None, f"Missing Terraform Cloud {arg}."
        # Return credentials args
        cmd += f" --{arg} {secret}"
    return cmd


ns = Collection("terraform")
ns.configure(CONFIG)
ns.add_task(update)
ns.add_task(run)
