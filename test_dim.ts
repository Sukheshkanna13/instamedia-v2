import 'dotenv/config';

async function test() {
    const apiKey = process.env.GEMINI_API_KEY;
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${apiKey}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            model: "models/gemini-embedding-001",
            content: { parts: [{ text: "Hello world" }] },
            outputDimensionality: 768
        })
    });
    const txt = await res.text();
    try {
        const json = JSON.parse(txt);
        console.log("Vector length:", json.embedding?.values?.length);
    } catch {
        console.log("Error body:", txt);
    }
}
test();
