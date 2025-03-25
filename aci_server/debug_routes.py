from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from pympler import muppy, summary
from integrations.common.auth import get_user_from_request
import objgraph
import gc
import time
import random
import os
from typing import List, Optional

router = APIRouter(prefix="/debug")

async def check_admin_user(request: Request):
    user_id = await get_user_from_request(request)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Check if user is the service account
    service_account_uid = os.environ.get("SERVICE_ACCOUNT_UID")
    
    if not service_account_uid:
        raise HTTPException(status_code=500, detail="SERVICE_ACCOUNT_UID not configured")
    
    if user_id != service_account_uid:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_id

def walk_ref_chain(obj, max_depth=5, seen=None):
    if seen is None:
        seen = set()

    if max_depth == 0 or id(obj) in seen:
        return []

    seen.add(id(obj))
    refs = gc.get_referrers(obj)
    chain = []

    for ref in refs:
        ref_type = type(ref).__name__
        # Optional: Skip noise like stack frames or trivial refs
        if ref_type in ["frame", "dict", "list", "tuple"]:
            continue
        chain.append({
            "ref_type": ref_type,
            "ref_str": str(ref)[:300],  # Snapshot of the ref content
            "child_chain": walk_ref_chain(ref, max_depth - 1, seen)
        })

    return chain

@router.get("/memory", dependencies=[Depends(check_admin_user)])
def memory_debug():
    all_objects = [o for o in muppy.get_objects() if "openai" not in str(type(o))]
    sum_obj = summary.summarize(all_objects)
    return {"summary": summary.format_(sum_obj)}

@router.get("/memory_trace", dependencies=[Depends(check_admin_user)])
def memory_trace():
    # Grab the biggest dicts
    biggest_dicts = objgraph.by_type('dict')[:5]
    trace_results = []

    for idx, obj in enumerate(biggest_dicts):
        refs = gc.get_referrers(obj)
        trace_results.append({
            "dict_id": id(obj),
            "size": len(obj),
            "referrers_count": len(refs),
            "referrers_types": [type(r).__name__ for r in refs]
        })

    return JSONResponse(content={"traces": trace_results})

@router.get("/memory_recursive", dependencies=[Depends(check_admin_user)])
def memory_recursive_trace():
    biggest_dicts = objgraph.by_type('dict')[:3]  # Limit to top 3 biggest dicts
    full_traces = []

    for obj in biggest_dicts:
        trace = {
            "dict_id": id(obj),
            "size": len(obj),
            "ref_chain": walk_ref_chain(obj, max_depth=4)
        }
        full_traces.append(trace)

    return JSONResponse(content={"ref_traces": full_traces})
