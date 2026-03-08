import 'dotenv/config';

async function test() {
    const apiKey = process.env.GEMINI_API_KEY;
    console.log("Key:", apiKey ? "Loaded" : "Missing");

    // Test native fetch
    const url = `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${apiKey}`;
    console.log("URL:", url.replace(apiKey || '', 'HIDDEN'));

    const bodyArgs = {
        model: "models/text-embedding-004",
        content: {
            parts: [{ text: "Hello world" }]
        }
    };

    try {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bodyArgs)
        });

        console.log("Status:", res.status);
        console.log("Response:", await res.text());
    } catch (e: any) {
        console.error("Fetch failed:", e.message);
    }
}
test();
