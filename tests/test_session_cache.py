from s3mapgen.session_cache import SessionGenerationCache,GenerationCacheKey

def key(i):return GenerationCacheKey(i,768,4,'upgraded','continental')
def test_lru_hit_and_eviction():
    c=SessionGenerationCache(2);c.put(key(1),'a');c.put(key(2),'b');assert c.get(key(1))=='a';c.put(key(3),'c');assert c.get(key(2)) is None;assert c.get(key(1))=='a';assert len(c)==2

def test_cache_clear():
    c=SessionGenerationCache(8);c.put(key(1),'a');c.clear();assert len(c)==0

from s3mapgen.session_cache import SessionStatsCache

class DummyState: pass

def test_stats_cache_reuses_same_state_and_evicts_lru():
    c=SessionStatsCache(2);a=DummyState();b=DummyState();d=DummyState()
    c.put(a,{'n':1});c.put(b,{'n':2})
    assert c.get(a)=={'n':1}
    c.put(d,{'n':3})
    assert c.get(b) is None
    assert c.get(a)=={'n':1} and c.get(d)=={'n':3}
