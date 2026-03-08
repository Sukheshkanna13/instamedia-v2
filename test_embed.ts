import { GoogleGenerativeAIEmbeddings } from "@langchain/google-genai";

async function run() {
    const embedder = new GoogleGenerativeAIEmbeddings({
        apiKey: process.env.GEMINI_API_KEY,
        model: "text-embedding-004",
    });
    console.log("Embedder initialized");
    try {
        const res = await embedder.embedDocuments(["Hello world"]);
        console.log("Result length:", res.length);
        if (res.length > 0) {
            console.log("Vector 0 length:", res[0].length);
        }
    } catch (e: any) {
        console.error("Error:", e.message);
    }
}
run();
