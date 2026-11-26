"""Joenell Studio Journal — short original story teasers that send readers to the full posts on joenellphotography.ca.
Rule: no couple names, ever. Only the couple in Chris & Lorena photos (no recognisable guest faces).
When the wedding site publishes the Sendall Gardens and Abkhazi Garden posts, change `url` + `cta` below and rebuild."""
JP = "https://www.joenellphotography.ca"

STORIES = [
    dict(
        slug="bowen-lookout-proposal", kind="Surprise proposal", place="Bowen Lookout · Cypress Mountain",
        title="A surprise proposal above Howe Sound",
        img="jh-cover",
        alt="A man on one knee proposing at Bowen Lookout, Cypress Mountain, with Howe Sound behind them",
        teaser="A ring, a mountain lookout and the whole of Howe Sound below. How we planned a surprise proposal at Bowen Lookout so the camera stayed hidden until the yes.",
        tips=["Plan the timing around the light and the crowds", "Pick the spot together before the day", "Keep the photographer out of sight until the question"],
        url=JP + "/blog/bowen-lookout-cypress-mountain-proposal", cta="Read the full story",
    ),
    dict(
        slug="english-bay-golden-hour", kind="Engagement session", place="English Bay · Stanley Park seawall",
        title="Golden hour on English Bay",
        img="cl-engagement-silhouette",
        alt="A couple in silhouette against a golden sunset over English Bay, Vancouver",
        teaser="Two silhouettes against a Vancouver sunset. When to arrive, where the seawall works best, and why the last twenty minutes of light are worth waiting for.",
        tips=["Arrive about an hour before sunset", "Face the sun for silhouettes", "Bring a warm layer for after the sun goes down"],
        url=JP + "/blog/stanley-park-wedding-engagement-photos", cta="Read the full story",
    ),
    dict(
        slug="sendall-gardens-engagement", kind="Engagement session", place="Sendall Gardens · Langley",
        title="Spring among the tulips in Langley",
        img="st-cover",
        alt="An engaged couple sitting on a garden bench among spring tulips at Sendall Gardens, Langley",
        teaser="Tulips, willows and a quiet garden bench. A relaxed spring engagement session at Sendall Gardens, and what to know before you plan one there.",
        tips=["Spring brings the tulips into bloom", "Light, soft colours suit the garden", "Weekday mornings are the quietest"],
        url=JP + "/engagements", cta="See engagement sessions",
    ),
    dict(
        slug="abkhazi-garden-wedding", kind="Wedding", place="Abkhazi Garden · Victoria",
        title="An autumn wedding at Abkhazi Garden",
        img="cl-wedding-cover",
        alt="A bride and groom kissing in an autumn garden at Abkhazi Garden, Victoria",
        teaser="A garden wedding on Vancouver Island in full autumn colour. What makes Abkhazi Garden special, and a few tips for a ceremony there.",
        tips=["Autumn colour peaks in October", "Plan portraits for the softer late-afternoon light", "Check the garden's own rules before you book"],
        url=JP + "/victoria-wedding-photographer", cta="Victoria wedding photography",
    ),
]
