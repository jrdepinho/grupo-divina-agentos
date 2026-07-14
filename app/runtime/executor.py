from .registry import get

def execute_plan(plan):

    results=[]

    for step in plan:

        fn=get(step["action"])

        if fn is None:

            results.append({
                "action":step["action"],
                "ok":False,
                "error":"Capability not registered"
            })

            continue

        try:

            r=fn(**step["args"])

            results.append({
                "action":step["action"],
                "ok":True,
                "result":r
            })

        except Exception as e:

            results.append({
                "action":step["action"],
                "ok":False,
                "error":str(e)
            })

    return results
