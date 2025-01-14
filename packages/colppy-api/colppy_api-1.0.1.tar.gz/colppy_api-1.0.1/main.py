import asyncio
from colppy.operations.main import ColppyAPIClient

async def main():
    client = ColppyAPIClient()
    await client.get_token()
    
    # Obtener todas las empresas excepto la especificada
    empresas = await client.get_empresas()
    print(empresas)

    await client.logout()

if __name__ == "__main__":
    asyncio.run(main())
