import { ChakraProvider } from "@chakra-ui/react";
import ChatInterface from "./components/ChatInterface";

function App() {
  return (
    <ChakraProvider>
      <div style={{ padding: 0 }}>
        <ChatInterface />
      </div>
    </ChakraProvider>
  );
}

export default App;
