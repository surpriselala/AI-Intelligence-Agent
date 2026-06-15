import { ChevronDown, SlidersHorizontal } from "lucide-react";

interface FilterBarProps {
  activeTopic: string;
  onTopicChange: (topic: string) => void;
}

const topics = ["All", "LLM", "Agent", "RAG", "Multimodal", "LangChain"];

export function FilterBar({ activeTopic, onTopicChange }: FilterBarProps) {
  return (
    <section className="filter-bar" aria-label="Dashboard filters">
      <div className="filter-group">
        {topics.map((topic) => (
          <button
            className={`filter-pill ${activeTopic === topic ? "active" : ""}`}
            key={topic}
            onClick={() => onTopicChange(topic)}
            type="button"
          >
            {topic}
          </button>
        ))}
        <button className="filter-pill more-pill" type="button">
          More
          <ChevronDown size={15} />
        </button>
      </div>
      <button className="sort-button" type="button">
        <SlidersHorizontal size={16} />
        Latest First
      </button>
    </section>
  );
}
