"""*Bankr* - Utils for development"""


def debugger() -> None:
    import debugpy

    debugpy.listen(5678)
    print("Waiting for debugger...")
    debugpy.wait_for_client()
    print("Debugger attached.")
