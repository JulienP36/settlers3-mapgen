from s3mapgen.session_cache import GenerationCacheKey, SessionGenerationCache


def key(seed):
    return GenerationCacheKey(seed=seed, side=768, players=4, mode='upgraded', archetype='continental')


def test_cache_reuses_and_promotes_entry():
    c=SessionGenerationCache(max_items=2)
    a=object();b=object()
    c.put(key(1),a);c.put(key(2),b)
    assert c.get(key(1)) is a
    assert [k.seed for k,_ in c.entries()]==[1,2]


def test_cache_is_lru_bounded_and_clearable():
    c=SessionGenerationCache(max_items=2)
    c.put(key(1),'a');c.put(key(2),'b');c.get(key(1));c.put(key(3),'c')
    assert c.get(key(2)) is None
    assert [k.seed for k,_ in c.entries()]==[3,1]
    c.clear()
    assert len(c)==0 and c.entries()==[]


def test_cache_key_distinguishes_generation_inputs():
    a=GenerationCacheKey(7,768,4,'legacy','continental')
    b=GenerationCacheKey(7,768,4,'upgraded','continental')
    c=GenerationCacheKey(7,768,4,'legacy','continental',('barebone',))
    assert len({a,b,c})==3
