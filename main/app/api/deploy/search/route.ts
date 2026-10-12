import { NextResponse } from 'next/server';
import { Index } from '@upstash/vector';
import OpenAI from 'openai';
import { VectorMatch, SearchResult, SearchResponse } from '@/app/modules/deploy/api/types.deploy';
import { EMBEDDING_MODEL, OPENROUTER_BASE_URL, openrouterHeaders } from '@/lib/ai/openrouter';

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: OPENROUTER_BASE_URL,
  defaultHeaders: openrouterHeaders,
});

const vectorIndex = new Index({
  url: process.env.UPSTASH_VECTOR_URL,
  token: process.env.UPSTASH_VECTOR_TOKEN,
});

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');
  
  if (!query || query.trim().length < 2) {
    return NextResponse.json<SearchResponse>({ results: [] });
  }

  try {
    const embeddingResponse = await openai.embeddings.create({
      model: EMBEDDING_MODEL,
      input: query.trim(),
    });
    
    const queryEmbedding = embeddingResponse.data[0].embedding;
    
    const searchResults = await vectorIndex.query({
      vector: queryEmbedding,
      topK: 20,
      includeMetadata: true,
    });
    
    const results: SearchResult[] = searchResults.map((match: VectorMatch) => ({
      id: match.metadata?.id,
      name: match.metadata?.name,
      github_url: match.metadata?.source_code_url,
      short_description: match.metadata?.short_description,
      score: match.score,
    })).filter(item => item.github_url);
    
    return NextResponse.json<SearchResponse>({ results });
  } catch (error) {
    console.error('Error searching repositories:', error);
    return NextResponse.json<SearchResponse>({ results: [], error: 'Failed to search repositories' }, { status: 500 });
  }
}
