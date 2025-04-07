export const formatAmountForStripe = (
  amount: number,
  currency: string
): number => {
  const currencies = ['USD', 'EUR', 'GBP'];
  const multiplier = currencies.includes(currency.toUpperCase()) ? 100 : 1;
  return Math.round(amount * multiplier);
};

export const formatAmountFromStripe = (
  amount: number,
  currency: string
): number => {
  const currencies = ['USD', 'EUR', 'GBP'];
  const divider = currencies.includes(currency.toUpperCase()) ? 100 : 1;
  return Math.round(amount) / divider;
};

export async function fetchPostJSON(url: string, data?: Record<string, unknown>): Promise<any> {
  try {
    const response = await fetch(url, {
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'follow',
      referrerPolicy: 'no-referrer',
      body: JSON.stringify(data || {}),
    });
    return await response.json();
  } catch (err) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw err;
  }
} 