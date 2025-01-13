/-
This is a d∃∀duction file providing first exercises about quantifiers and numbers.
French version.
-/

-- Lean standard import
import data.real.basic
import tactic
import data.finset
import topology.sequences
import data.nat.basic


-- dEAduction tactics
-- structures2 and utils are vital
import deaduction_all_tactics
-- import structures2      -- hypo_analysis, targets_analysis
-- import utils            -- no_meta_vars
-- import compute_all      -- Tactics for the compute buttons
-- import push_neg_once    -- Pushing negation just one step
-- import induction        -- Induction theorems

-- dEAduction definitions
-- import set_definitions
-- import real_definitions

-- Use classical logic
local attribute [instance] classical.prop_decidable

axiom h: (∀X: Type, ∀ A : finset X, ∃ x: X, x ∉ A)

-- Définir une suite par récurrence I
def u : ℕ → ℕ 
  | 0 := 0
  | (n + 1) := (u n) + 4
#eval (u 4)


-- Définir une suite par récurrence II
def v : ℕ→ ℕ :=  λ n, (nat.rec_on n 0 (λ n un, un + 4))  
#eval (v 4)



lemma example1 (X: Type) (H: (∀ A: finset X, ∃ x: X, x ∉ A)):
(∃ u: ℕ → X, ∀k l, k<l → (u k ≠ u l)) :=
begin
  -- set u:ℕ→ X :=
  -- |n := classical.axiom_of_choice (h X),

  -- set u:ℕ→ ℕ := λ n, n+1,
-- let u : ℕ → ℕ :=
--   | 0 := 0
--   | (n + 1) := 0

set u: ℕ→ ℕ := λ n, (nat.rec_on n 0 (λ n un, n)) with h1,  
end

constant X : Type
constant P (x y: X) : Prop
constant HP : ∀A: finset X, ∃y, ∀x ∈ A, P x y 

example : ∃ u : ℕ → X, ∀ k l, k < l → P (u k) (u l) :=
begin
  have u: ℕ → ℕ := 
 
end



lemma example2 (X: Type) (H: (∀ A: finset X, ∃ x: X, x ∉ A)):
  (∃ u: ℕ → X, ∀k l, k<l → (u k ≠ u l)) :=
begin
--   classical,
  choose next hnext using H,
  let f := λ (s : finset X), insert (next s) s,
  let sets := λ n, nat.iterate f n ∅,
  existsi next ∘ sets,
  sorry
end









