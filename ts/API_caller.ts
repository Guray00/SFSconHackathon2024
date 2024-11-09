import fetch from 'cross-fetch'; // cross-fetch è compatibile con CommonJS e ESM

async function fetchDataFromEndpoint(baseUrl: string, params: Record<string, string>): Promise<void> {
  try {
    const url = new URL(baseUrl);
    //if to check if the params are empty and in that case perform the query without them
    if (Object.keys(params).length === 0) {
      console.log("URL completo:", url.toString());
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`Errore nella richiesta: ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Dati ricevuti:", data);
      return;
    } 
    Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, value));

    console.log("URL completo:", url.toString());

    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`Errore nella richiesta: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("Dati ricevuti:", data);
    
  } catch (error) {
    console.error("Errore durante la richiesta:", error);
  }
}
  
    // Esempio di utilizzo della funzione con un endpoint e alcuni parametri
    fetchDataFromEndpoint("http://localhost:5000/GetAveragePrice", {
        start_city: "Milan",
        end_city: "Lyon"
    });

    // Esempio di utilizzo della funzione con un endpoint e alcuni parametri
    fetchDataFromEndpoint("http://localhost:5000/GetAvailableCities", {
      });

    // Esempio di utilizzo della funzione con un endpoint e alcuni parametri
    fetchDataFromEndpoint("http://localhost:5000/negotiations", {

    });    
  
