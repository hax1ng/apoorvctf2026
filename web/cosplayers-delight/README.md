# Cosplayer's Delight

**Category:** Web | **Difficulty:** Medium | **Flag:** `apoorvctf{gr4Ph_l34k5_r3v34l_v1cT0r5_l45t_v0t35_7f2a9}`

## Overview
A popularity poll web app at ComicCon where you need to identify "Target V" and find the 5 targets he voted for most recently.

## Solution

1. **Recon:** The app runs on FastAPI/Uvicorn with a login/register system and voting leaderboard. An HTML comment hints at user `test` having a weak password (`test:test`).

2. **API Discovery:** FastAPI's `/docs` endpoint exposes the OpenAPI spec, revealing hidden endpoints: `/flag` (takes a `votes` array parameter), `/hidden_flag`, `/admin`, `/stats`, and `/user/{username}`.

3. **Identify Target V:** User `victor` has the bio "i only vote for the real ones" — he's Target V.

4. **Leak Victor's votes:** The `/vote_for` endpoint response includes `recent_voters` for the target user (an information leak noted in the API description). By voting for every user on the leaderboard and checking if `victor` appears in their `recent_voters`, we identify all 25 users Victor voted for, along with timestamps.

5. **Extract the last 5:** The `/flag` endpoint requires exactly 5 usernames. Sorting Victor's votes chronologically and submitting the last 5 (`emilysys`, `devon.`, `judy`, `dave`, `alice`) returns the real flag.

The decoy flags (`n07_3n0ugh_v0735_n33d_5_44ab` and `n3v3r_g0nn4_g1v3_y0u_up_dQw4w9`) are red herrings on `/flag` (wrong votes) and `/hidden_flag`/`/admin`.

## Key Takeaways
- Always check `/docs` and `/openapi.json` on FastAPI apps for hidden endpoints.
- API responses can leak information (recent_voters) that enables graph analysis of voting relationships.
- HTML comments often contain credential hints in CTFs.
- Decoy flags are common — verify the flag makes sense contextually.
