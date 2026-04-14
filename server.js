import "dotenv/config"
import express from "express"
import Stripe from "stripe"
import cors from "cors"
import { join, dirname } from "path"
import { fileURLToPath } from "url"
import { scoreAssessment } from "./engine/scoreAssessment.js"
import { generateMiniProfile } from "./engine/miniProfileGenerator.js"
import OpenAI from "openai"

// ✅ CLEAN DEBUG (not the entire env dump chaos)
console.log("ENV CHECK:", {
  OPENAI_API_KEY: !!process.env.OPENAI_API_KEY,
  STRIPE_SECRET_KEY: !!process.env.STRIPE_SECRET_KEY,
  SITE_URL: process.env.SITE_URL,
})

// ✅ SAFE INIT (no crash if missing)
const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null

const stripe = process.env.STRIPE_SECRET_KEY
  ? new Stripe(process.env.STRIPE_SECRET_KEY)
  : null

const __dirname = dirname(fileURLToPath(import.meta.url))
const SUBMISSIONS_DIR = join(__dirname, "submissions")

// Vercel serverless: filesystem writes not supported, skip mkdir
// await mkdir(SUBMISSIONS_DIR, { recursive: true })

const app = express()
app.use(cors())
app.use(express.json())

const SITE_URL = process.env.SITE_URL || "http://localhost:5173"

// ---------------- SAVE ----------------
async function saveSubmission(type, data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
  const safeName = (data.name || "unknown")
    .replace(/[^a-zA-Z0-9]/g, "_")
    .slice(0, 30)

  const filename = `${type}_${safeName}_${timestamp}.json`
  const filepath = join(SUBMISSIONS_DIR, filename)

  const record = {
    type,
    submittedAt: new Date().toISOString(),
    ...data,
  }

  // Vercel serverless: filesystem writes disabled, log only
  console.log("SAVED SUBMISSION:", record)
  // await writeFile(filepath, JSON.stringify(record, null, 2))
  
  return { filename, submittedAt: record.submittedAt }
}

// ---------------- BASIC ROUTES ----------------
app.get("/", (req, res) => {
  res.json({
    status: "alive",
    openai: !!process.env.OPENAI_API_KEY,
    stripe: !!process.env.STRIPE_SECRET_KEY,
  })
})

// ---------------- PROFILE ----------------
app.post("/submit/profile", async (req, res) => {
  try {
    const { name, email, answers, questions } = req.body

    if (!answers?.length) {
      return res.status(400).json({ error: "No answers provided" })
    }

    const result = await saveSubmission("profile", { name, email, answers, questions })
    res.json({ success: true, ...result })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// ---------------- REAL ESTATE ----------------
app.post("/submit/real-estate", async (req, res) => {
  try {
    const { name, email, phone, promoCode, answers, questions } = req.body

    if (!answers?.length) {
      return res.status(400).json({ error: "No answers provided" })
    }

    const result = await saveSubmission("real-estate", {
      name,
      email,
      phone,
      promoCode,
      answers,
      questions,
    })

    res.json({ success: true, ...result })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// ---------------- INTERPRET ----------------
app.post("/api/interpret", async (req, res) => {
  try {
    if (!openai) {
      return res.status(500).json({
        ok: false,
        error: "OpenAI not configured",
      })
    }

    const { setId, responses } = req.body

    if (!setId || !responses?.length) {
      return res.status(400).json({ ok: false, error: "Missing data" })
    }

    const scoring = scoreAssessment(setId, responses)

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "Return JSON only." },
        { role: "user", content: JSON.stringify(scoring) },
      ],
    })

    const raw = completion.choices[0].message.content.trim()

    let interpretation
    try {
      interpretation = JSON.parse(raw)
    } catch {
      interpretation = { raw }
    }

    res.json({
      ok: true,
      scoring,
      interpretation,
    })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message })
  }
})

// ---------------- STRIPE ----------------
app.post("/create-checkout-session", async (req, res) => {
  try {
    if (!stripe) {
      return res.status(500).json({ error: "Stripe not configured" })
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],
      mode: "payment",
      line_items: [
        {
          price: process.env.STRIPE_PRICE_ID,
          quantity: 1,
        },
      ],
      success_url: `${SITE_URL}/success`,
      cancel_url: `${SITE_URL}/`,
    })

    res.json({ url: session.url })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// ---------------- MINI PROFILE ----------------
app.post("/api/moremindmap/mini-profile", async (req, res) => {
  try {
    const { answers } = req.body

    if (!answers || typeof answers !== "object") {
      return res.status(400).json({ success: false })
    }

    const responses = Object.entries(answers).map(([id, answer]) => ({
      questionId: parseInt(id),
      type: "multiple_choice",
      answer,
    }))

    const scoring = scoreAssessment("set_1", responses)

    const miniProfile = generateMiniProfile(scoring)

    await saveSubmission("mini-profile", { answers, scoring })

    res.json({
      success: true,
      scoringPayload: {
        ...scoring,
        ranked_dimensions: scoring.ranked,
      },
      miniProfile,
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    })
  }
})

// ---------------- START ----------------
app.listen(4242, () => console.log("Server running"))