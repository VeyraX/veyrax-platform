import { generateObject } from 'ai';
import { createClient } from '@/lib/utils/supabase/server';
import { flow_improvement_prompt } from '@/app/prompts/flow_improvements_prompt';
import { NextResponse } from 'next/server';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const flowSchema = z.object({
  name: z.string().describe('Название рабочего процесса'),
  description: z.string().describe('Детальное описание рабочего процесса')
});

export async function POST(request: Request) {
  try {
    const { description, name } = await request.json();
    
    if (!description) {
      return NextResponse.json(
        { error: 'Description is required' }, 
        { status: 400 }
      );
    }
    
    const supabase = createClient();
    const { data: actions, error } = await supabase
      .from('provider_actions')
      .select('provider_id, provider_name, action_name, logo_url');
    
    if (error) {
      return NextResponse.json(
        { error: 'Failed to fetch available actions' }, 
        { status: 500 }
      );
    }
    
    const systemMessage = `
      ${flow_improvement_prompt}
      
      Available tools:
      ${actions.map(action => 
        `- ${action.action_name} (Provider: ${action.provider_name}, Logo URL: ${action.logo_url})`
      ).join('\n')}
      
      You MUST only use these specific tools in your suggestions. Do not invent new tools.
      
      Improve the workflow description by adding structure, details, and suggesting appropriate tools from the available list.
      If a name is provided, use that name. Otherwise create an appropriate name based on the workflow description.
      
      IMPORTANT: When referring to an action in the description, use this EXACT HTML format:
      <span class="inline-flex items-center gap-1 bg-white border border-gray-200 rounded-md px-1 py-0.5 mx-0.5 action-item shadow-sm" contenteditable="false" data-provider="[PROVIDER_NAME]" data-action="[ACTION_NAME]">
        <div class="h-3.5 w-3.5 rounded-sm overflow-hidden flex items-center justify-center bg-white">
          <img src="[LOGO_URL]" alt="[ACTION_NAME]" class="max-h-full max-w-full object-contain">
        </div>
        <span class="text-primary text-xs font-medium">[ACTION_NAME]</span>
      </span>
    `;
    
    const result = await generateObject({
      model: openai('gpt-4o'),
      system: systemMessage,
      prompt: `Here is my workflow${name ? ` with name "${name}"` : ''}. Please improve it:\n\n${description}`,
      schema: flowSchema
    });

    // Проверяем и обрабатываем результат
    let responseObject;
    
    if (result && typeof result === 'object' && result.object) {
      responseObject = {
        name: result.object.name || name || 'Untitled Flow',
        description: result.object.description || description
      };
    } else {
      responseObject = {
        name: name || 'Untitled Flow',
        description: description
      };
    }
    
    console.log('Improved flow:', responseObject.name);
    
    return NextResponse.json(responseObject);
    
  } catch (error) {
    console.error('Error improving description:', error);
    return NextResponse.json(
      { error: 'Failed to improve description' }, 
      { status: 500 }
    );
  }
}
