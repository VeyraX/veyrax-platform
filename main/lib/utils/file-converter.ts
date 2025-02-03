import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import mammoth from 'mammoth';


export async function convertTableFileToMarkdown(file: File): Promise<string> {
  const fileType = file.name.split('.').pop()?.toLowerCase();

  if (fileType === 'csv') {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        complete: (results) => {
          const markdown = convertDataToMarkdown(results.data as any[][]);
          resolve(markdown);
        },
        error: (error) => reject(error)
      });
    });
  }

  if (['xlsx', 'xls'].includes(fileType || '')) {
    const data = await readFileAsArrayBuffer(file);
    const workbook = XLSX.read(data, { type: 'array' });
    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
    const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
    return convertDataToMarkdown(jsonData as any[][]);
  }

  throw new Error('Unsupported file type');
}

function convertDataToMarkdown(data: any[][]): string {
  if (!data.length) return '';

  const cleanData = data.map(row => 
    row.map(cell => 
      String(cell)
        .replace(/\|/g, '\\|')
        .trim()
    )
  );

  const headers = cleanData[0];
  const columnCount = headers.length;
  
  let markdown = '| ' + headers.join(' | ') + ' |\n';
  markdown += '|' + Array(columnCount).fill(' --- ').join('|') + '|\n';
  
  for (let i = 1; i < cleanData.length; i++) {
    const row = cleanData[i];
    while (row.length < columnCount) {
      row.push('');
    }
    markdown += '| ' + row.slice(0, columnCount).join(' | ') + ' |\n';
  }

  return String(markdown.trim());
}

export async function convertTextFileToString(file: File): Promise<string> {
  const fileType = file.name.split('.').pop()?.toLowerCase();

  switch (fileType) {
    case 'txt':
    case 'doc':
    case 'rtf':
      return readFileAsText(file);

    case 'docx': {
      const arrayBuffer = await readFileAsArrayBuffer(file);
      const result = await mammoth.extractRawText({ arrayBuffer });
      return result.value;
    }

    case 'pdf': {
      const text = await readFileAsText(file);
      return text
        .replace(/[\r\n]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    }

    default:
      throw new Error('Unsupported text file type');
  }
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result as string);
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

function readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result as ArrayBuffer);
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}