import { useState, useRef, useEffect } from "react";
import { Heading, Box, VStack, Input, Button, Text, Select, Flex, Spinner, useToast } from "@chakra-ui/react";
import axios from "axios";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import React from "react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SIZE = 8; // margin for titles
const PADDING = "15%";
const bg_color = "rgb(249,250,246)";
const chat_color = "rgb(241,242,238)";
const mistral_orange = "rgb(250,80,14,255)";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function renderMessageContent(content: string) {
  const codeBlockRegex = /```([a-z]*)\n([\s\S]*?)```/g;

  // Deal with code blocks to show them correctly
  if (codeBlockRegex.test(content)) {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;
    codeBlockRegex.lastIndex = 0; // reset regex

    while ((match = codeBlockRegex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        const markdownChunk = content.slice(lastIndex, match.index);
        parts.push(
          <ReactMarkdown
            key={`md-${lastIndex}`}
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => (
                <Heading size="xl" mt={SIZE}>
                  {children}
                </Heading>
              ),
              h2: ({ children }) => (
                <Heading size="lg" mt={SIZE}>
                  {children}
                </Heading>
              ),
              h3: ({ children }) => (
                <Heading size="md" mt={SIZE}>
                  {children}
                </Heading>
              ),
              h4: ({ children }) => (
                <Heading size="sm" mt={SIZE}>
                  {children}
                </Heading>
              ),
              p: ({ children }) => <Text mb={2}>{children}</Text>,
              strong: ({ children }) => <Text as="strong">{children}</Text>,
              ul: ({ children }) => (
                <Box as="ul" pl={5} style={{ listStyleType: "disc", listStylePosition: "inside" }}>
                  {children}
                </Box>
              ),
              ol: ({ children }) => (
                <Box as="ol" pl={5} style={{ listStyleType: "decimal", listStylePosition: "inside" }}>
                  {children}
                </Box>
              ),
              li: ({ children }) => <Box as="li">{children}</Box>,
            }}
          >
            {markdownChunk}
          </ReactMarkdown>
        );
      }

      function wrapCodeLines(code, maxLen) {
        return code
          .split("\n")
          .map((line) => (line.length > maxLen ? line.match(new RegExp(".{1," + maxLen + "}", "g")).join("\n") : line))
          .join("\n");
      }

      const language = match[1] || "text";
      const code = match[2];
      parts.push(
        <SyntaxHighlighter
          key={`code-${match.index}`}
          language={language}
          style={vscDarkPlus}
          customStyle={{
            borderRadius: 8,
            margin: "12px 0",
            whiteSpace: "pre-wrap", // <-- wrap lines
            wordBreak: "break-all",
            maxWidth: "100%",
          }}
          showLineNumbers
        >
          {wrapCodeLines(code, 82)}
        </SyntaxHighlighter>
      );
      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < content.length) {
      const markdownChunk = content.slice(lastIndex);
      parts.push(
        <ReactMarkdown
          key={`md-${lastIndex}`}
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => (
              <Heading size="xl" mt={SIZE}>
                {children}
              </Heading>
            ),
            h2: ({ children }) => (
              <Heading size="lg" mt={SIZE}>
                {" "}
                {children}
              </Heading>
            ),
            h3: ({ children }) => (
              <Heading size="md" mt={SIZE}>
                {children}
              </Heading>
            ),
            h4: ({ children }) => (
              <Heading size="sm" mt={SIZE}>
                {children}
              </Heading>
            ),
            p: ({ children }) => <Text mb={2}>{children}</Text>,
            strong: ({ children }) => <Text as="strong">{children}</Text>,
            ul: ({ children }) => (
              <Box as="ul" pl={5} style={{ listStyleType: "disc", listStylePosition: "inside" }}>
                {children}
              </Box>
            ),
            ol: ({ children }) => (
              <Box as="ol" pl={5} style={{ listStyleType: "decimal", listStylePosition: "inside" }}>
                {children}
              </Box>
            ),
            li: ({ children }) => <Box as="li">{children}</Box>,
          }}
        >
          {markdownChunk}
        </ReactMarkdown>
      );
    }

    return parts;
  }

  // Sinon, on rend tout en markdown classique
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <Heading size="xl" mt={SIZE}>
            {children}
          </Heading>
        ),
        h2: ({ children }) => (
          <Heading size="lg" mt={SIZE}>
            {children}
          </Heading>
        ),
        h3: ({ children }) => (
          <Heading size="md" mt={SIZE}>
            {children}
          </Heading>
        ),
        h4: ({ children }) => (
          <Heading size="sm" mt={SIZE}>
            {children}
          </Heading>
        ),
        p: ({ children }) => <Text mb={0}>{children}</Text>,
        strong: ({ children }) => <Text as="strong">{children}</Text>,
        ul: ({ children }) => (
          <Box as="ul" pl={5} style={{ listStyleType: "disc", listStylePosition: "inside" }}>
            {children}
          </Box>
        ),
        ol: ({ children }) => (
          <Box as="ol" pl={5} style={{ listStyleType: "decimal", listStylePosition: "inside" }}>
            {children}
          </Box>
        ),
        li: ({ children }) => (
          <Box as="li" mt={2}>
            {children}
          </Box>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("mistral-large-latest");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  useEffect(() => {
    fetchModels();
  }, []);

  const handleReload = async () => {
    try {
      setIsLoading(true);

      await axios.post("http://localhost:8000/api/reset");
      setMessages([]); // Reset messages
      await fetchModels(); // Reload models
      toast({
        title: "Rechargement effectué",
        status: "success",
        duration: 2000,
        isClosable: true,
      });
    } catch (error: unknown) {
      toast({
        title: "Erreur lors du rechargement",
        description: error instanceof Error ? error.message : "Une erreur est survenue",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/models");
      setModels(response.data.models);
    } catch (error: unknown) {
      toast({
        title: "Erreur lors du chargement des modèles",
        description: error instanceof Error ? error.message : "Une erreur est survenue",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/api/chat", {
        message: input,
        model: selectedModel,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: unknown) {
      let description = "Une erreur est survenue";
      if (axios.isAxiosError(error)) {
        // If backend send a detailed error response
        description = error.response?.data?.detail || error.message || "Une erreur est survenue";
        if (description.includes("Service tier capacity")) {
          description = "Trop de messages. Veuillez réessayer dans quelques instants.";
        }
      } else if (error instanceof Error) {
        description = error.message;
      }
      toast({
        title: "Erreur lors de l'envoi du message",
        description,
        status: "error",
        duration: 8000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      display="flex"
      flexDirection="column"
      overflow="hidden"
      bg="white"
    >
      <Box w="100%" p={4} bg={bg_color} borderBottom="1px" borderColor="gray.200">
        <Flex justify="flex-start">
          <Button onClick={handleReload} colorScheme="gray" isLoading={isLoading}>
            Recharger
          </Button>
        </Flex>
      </Box>

      <Box flex={1} p={PADDING} overflowY="auto" bg={bg_color}>
        {messages.map((message, index) => (
          <Flex key={index} justify={message.role === "user" ? "flex-end" : "flex-start"} mb={10}>
            <Box
              pl={2}
              pr={2}
              borderRadius="30px"
              bg={message.role === "user" ? chat_color : ""}
              maxW={message.role === "user" ? "80%" : "95%"}
              color="blue.500"
            >
              <Box color="white" p={4}>
                <Flex align="center" gap={3}>
                  {message.role === "assistant" ? (
                    <Box bg={mistral_orange} borderRadius="30%" p={1} display="inline-block" alignSelf="flex-start">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 298.24155 298.24154"
                        width="28"
                        height="28"
                        fill="currentColor"
                      >
                        <polygon
                          points="242.424,90.909 242.424,121.212 212.121,121.212 212.121,151.515 181.818,151.515 181.818,121.212 151.515,121.212 151.515,90.909 121.212,90.909 121.212,212.121 90.909,212.121 90.909,242.424 181.818,242.424 181.818,212.121 151.515,212.121 151.515,181.818 181.818,181.818 181.818,212.121 212.121,212.121 212.121,181.818 242.424,181.818 242.424,212.121 212.121,212.121 212.121,242.424 303.03,242.424 303.03,212.121 272.727,212.121 272.727,90.909"
                          transform="translate(-47.848728,-17.545727)"
                        />
                      </svg>
                    </Box>
                  ) : null}

                  {message.role === "assistant" ? (
                    <Text color="gray.900">{renderMessageContent(message.content)}</Text>
                  ) : (
                    <Text color="gray.900">{message.content}</Text>
                  )}
                </Flex>
              </Box>
            </Box>
          </Flex>
        ))}
        {isLoading && (
          <Flex justify="center" my={4}>
            <Spinner />
          </Flex>
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Box pl={PADDING} pr={PADDING} pb={4} pt={4} bg={bg_color} borderTop="1px" borderColor="gray.200">
        <form onSubmit={handleSubmit}>
          <Flex gap={2}>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Demander au Chat"
              disabled={isLoading}
              bg="white"
              size="lg"
            />
            <Button type="submit" colorScheme="orange" isLoading={isLoading} size="lg">
              Envoyer
            </Button>
          </Flex>
        </form>
      </Box>
    </Box>
  );
};

export default ChatInterface;
