# conversational-agent-for-mindful-eating

# Note on Instagram Business Access Token

Used by this app to access public content from a target Instagram Business or Creator account
(e.g., to fetch the most recent post, caption, and media for comment generation).

Who needs this:
- YOU (the developer), not the personas
- This token is tied to your Facebook user who manages the IG account you're pulling posts from

When to use it:
- On startup, to fetch the latest Instagram post and related content
- Pass it into the Instagram Graph API when accessing someone else's business content

Token details:
- It's a long-lived token (valid ~60 days)
- Refresh it every 50 days using your current token, app ID, and app secret
- If it expires before refresh, you'll need to re-authenticate via OAuth and repeat the token exchange
