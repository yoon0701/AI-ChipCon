import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./PersonaSelect.module.css";

function PersonaSelect() {
  const navigate = useNavigate();

  const personas = [
    { id: "doctor", name: "의사 선생님", img: "/doctor.png" },
    { id: "herbalist", name: "한의사", img: "/herbalist.png" },
    { id: "trainer", name: "헬스 트레이너", img: "/trainer.png" },
  ];

  const handleSelect = (id) => {
    localStorage.setItem("persona", id);
    navigate("/home");
  };

  return (
    <div className={styles.container}>
      <img src="/logo.png" alt="logo" className={styles.logo} />
      <h2 className={styles.title}>상담을 원하는 페르소나를 선택하세요</h2>
      <div className={styles.personas}>
        {personas.map((p) => (
          <div key={p.id} className={styles.personaCard} onClick={() => handleSelect(p.id)}>
            <img src={p.img} alt={p.name} />
            <p>{p.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PersonaSelect;
