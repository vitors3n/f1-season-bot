"""Utilitários para manter dados em cache durante falhas temporárias das APIs."""


def chave_cache_expirado(chave):
    return f"stale:{chave}"


async def buscar_com_cache(cache, chave, ttl, buscar, logger, descricao):
    """Obtém dados recentes ou reutiliza a última resposta em caso de falha."""
    dados = cache.get(chave)
    if dados is not None:
        logger.debug("%s obtido do cache", descricao)
        return dados

    dados = await buscar()
    if dados is not None:
        cache.set(chave, dados, expire=ttl)
        cache.set(chave_cache_expirado(chave), dados)
        logger.info("%s atualizado pela API", descricao)
        return dados

    dados_expirados = cache.get(chave_cache_expirado(chave))
    if dados_expirados is not None:
        logger.warning("Falha na API; reutilizando %s expirado do cache", descricao)
        return dados_expirados
    return None
