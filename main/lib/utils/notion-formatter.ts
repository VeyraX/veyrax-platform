export const formatProperties = (
    title?: string,
    text?: string,
    date?: string,
    status?: string,
    number?: number,
    checkbox?: boolean,
    properties: Record<string, any> = {}
  ) => {
    return {
      ...properties,
      ...(title && {
        "Name": {
          "title": [{ "text": { "content": title } }]
        }
      }),
      ...(text && {
        "Description": {
          "rich_text": [{ "text": { "content": text } }]
        }
      }),
      ...(date && {
        "Date": {
          "date": { "start": date }
        }
      }),
      ...(status && {
        "Status": {
          "select": { "name": status }
        }
      }),
      ...(number !== undefined && {
        "Number": {
          "number": number
        }
      }),
      ...(checkbox !== undefined && {
        "Checkbox": {
          "checkbox": checkbox
        }
      })
    };
  };
  
  export const formatDatabaseFilter = ({
    title,
    date,
    dateAfter,
    dateBefore,
    status,
    checkbox,
    number,
    numberGreater,
    numberLess,
    filter = {}
  }: {
    title?: string;
    date?: string;
    dateAfter?: string;
    dateBefore?: string;
    status?: string;
    checkbox?: boolean;
    number?: number;
    numberGreater?: number;
    numberLess?: number;
    filter?: Record<string, any>;
  }) => {
    if (Object.keys(filter).length > 0) return filter;
  
    if (title) {
      return {
        property: "Name",
        title: { contains: title }
      };
    }
  
    if (date) {
      return {
        property: "Date",
        date: { equals: date }
      };
    }
  
    if (dateAfter || dateBefore) {
      return {
        property: "Date",
        date: {
          ...(dateAfter && { after: dateAfter }),
          ...(dateBefore && { before: dateBefore })
        }
      };
    }
  
    if (status) {
      return {
        property: "Status",
        select: { equals: status }
      };
    }
  
    if (checkbox !== undefined) {
      return {
        property: "Checkbox",
        checkbox: { equals: checkbox }
      };
    }
  
    if (number !== undefined || numberGreater !== undefined || numberLess !== undefined) {
      return {
        property: "Number",
        number: {
          ...(number !== undefined && { equals: number }),
          ...(numberGreater !== undefined && { greater_than_or_equal_to: numberGreater }),
          ...(numberLess !== undefined && { less_than_or_equal_to: numberLess })
        }
      };
    }
  
    return {};
  };
  
  export const formatSort = (
    sortBy?: string,
    sortDirection?: 'ascending' | 'descending',
    sorts?: Record<string, any>[]
  ) => {
    if (sorts) return sorts;
    
    if (sortBy) {
      return [{
        property: sortBy,
        direction: sortDirection || 'ascending'
      }];
    }
  
    return undefined;
  };