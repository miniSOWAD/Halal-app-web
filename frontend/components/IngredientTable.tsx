import type { IngredientResult } from "@/lib/types";

function statusClass(status: string) {
  if (status === "HALAL" || status === "HEALTHY") return "good";
  if (status === "HARAM" || status === "UNHEALTHY") return "bad";
  if (status === "DOUBTFUL") return "warn";
  return "neutral";
}

export default function IngredientTable({ ingredients }: { ingredients: IngredientResult[] }) {
  if (!ingredients.length) return <p className="muted">No ingredients were extracted.</p>;
  return (
    <div className="table-wrap">
      <table className="ingredient-table">
        <thead>
          <tr>
            <th>Ingredient</th>
            <th>Halal status</th>
            <th>Health note</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ingredient, index) => (
            <tr key={`${ingredient.name}-${index}`}>
              <td><strong>{ingredient.name}</strong>{!ingredient.matched && <small> Not in database</small>}</td>
              <td><span className={`status-pill ${statusClass(ingredient.status)}`}>{ingredient.status}</span></td>
              <td>{ingredient.health_status}</td>
              <td>{ingredient.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
