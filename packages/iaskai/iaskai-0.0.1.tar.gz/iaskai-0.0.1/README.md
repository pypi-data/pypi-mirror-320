# IAskAI Client

```python
import asyncio
import iask

client = iask.Client()

async def main():
    async for chunk in client.ask({
        'mode': 'wiki',
        'q': 'When Symfony 7.2 release?'
    }):
        print(chunk, end='')

asyncio.run(main())
```