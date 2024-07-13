import { GoogleGenerativeAI } from '@google/generative-ai';
import { NextRequest, NextResponse } from 'next/server';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function POST(request: NextRequest) {
  const { message } = await request.json();
  
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-flash-1.5" });
    const result = await model.generateContent(message);
    const response = await result.response;
    const text = response.text();
    
    return NextResponse.json({ reply: text });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ error: 'An error occurred while processing your request.' }, { status: 500 });
  }
}