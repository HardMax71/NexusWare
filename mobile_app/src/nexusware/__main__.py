from nexusware.app import main

if __name__ == '__main__':
    app = main()
    # For toga apps we use regular main_loop() instead of asyncio.run()
    app.main_loop()
