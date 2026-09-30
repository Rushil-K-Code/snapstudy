# SnapStudy report: lecture.txt

_Generated 100% offline. Provider: CPUExecutionProvider. NLP time: 0.6 ms._

## Summary
- First normal form requires that every column holds atomic values and that each row is unique.
- Second normal form removes partial dependencies, meaning every non-key attribute must depend on the whole primary key.
- Third normal form removes transitive dependencies so that non-key attributes depend only on the key.
- A primary key is a column or set of columns that uniquely identifies each row in a table.
- A foreign key is a column that references the primary key of another table and enforces referential integrity.

## Flashcards
**Q1.** What is Database normalization?
> the process of organizing a relational database to reduce data redundancy and improve integrity.

**Q2.** What is A primary key?
> a column or set of columns that uniquely identifies each row in a table.

**Q3.** What is A foreign key?
> a column that references the primary key of another table and enforces referential integrity.

**Q4.** What is Denormalization?
> the deliberate introduction of redundancy to speed up read-heavy queries.

**Q5.** Fill in the blank: Second normal form removes partial dependencies, meaning every non-_____ attribute must depend on the whole primary key.
> key

**Q6.** Fill in the blank: A foreign key is a column that references the primary key of another table and enforces referential _____.
> integrity

**Q7.** Fill in the blank: Third _____ form removes transitive dependencies so that non-key attributes depend only on the key.
> normal

**Q8.** Fill in the blank: First normal _____ requires that every column holds atomic values and that each row is unique.
> form

## Transcript

Database normalization is the process of organizing a relational database to reduce data redundancy and improve integrity. First normal form requires that every column holds atomic values and that each row is unique. Second normal form removes partial dependencies, meaning every non-key attribute must depend on the whole primary key. Third normal form removes transitive dependencies so that non-key attributes depend only on the key. A primary key is a column or set of columns that uniquely identifies each row in a table. A foreign key is a column that references the primary key of another table and enforces referential integrity. Denormalization is the deliberate introduction of redundancy to speed up read-heavy queries. Students often over-normalize schemas, which leads to many joins and slower reports. Good design balances integrity against performance for the actual workload. Indexes speed up lookups but slow down writes because they must be updated on every insert.