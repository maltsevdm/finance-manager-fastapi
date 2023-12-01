import React, { useState, useEffect } from "react";
import './styles/App.css'
import SummaryBlock from "./components/SummaryBlock/SummaryBlock.jsx";
import CategoryList from "./components/CategoryList/CategoryList.jsx";
import Modal from "./components/modal/modal.jsx";
import userEvent from "@testing-library/user-event";
import {sendGet} from "./utils.js";
import {url_categories, url_icons, url_icon} from "./config.js";
import CategoryService from "./API/CategoryService.js";

function App() {
  const [categoryFrom, setCategoryFrom] = useState(null)
  const [categoryTo, setCategoryTo] = useState(null)
  const [modalActive, setModalActive] = useState(false)
  const [sumData, setSumData] = useState({
      balance: 6000, exp: 2000, inc: 7000
  })
  
  const [categoryListExpense, setCategoryListExpense] = useState([])
  const [categoryListIncome, setCategoryListIncome] = useState([])

  async function fetchCategories () {
    const catExp = await CategoryService.getExpense()
    setCategoryListExpense(catExp)

    const catInc = await CategoryService.getIncome()
    setCategoryListIncome(catInc)
  }

  useEffect(() => {
      fetchCategories()
    }, [])


  function addOperation (e) {
      setModalActive(false)
      const amountInput = document.querySelector('.amount')
      const amount = Number(amountInput.value)
      console.log('from ' + categoryFrom + ' to ' + categoryTo + '. Amount: ' + amount)
      amountInput.value = "" 
      setSumData({
          balance: sumData.balance - amount,
          exp: sumData.exp + amount,
          inc: sumData.inc
      })

      for (let i = 0; i < categoryListExpense.length; i++) {
          if (categoryListExpense[i].name === categoryTo) {
            categoryListExpense[i].sum = categoryListExpense[i].sum + amount
            break
          }
      }
      setCategoryListExpense(categoryListExpense)

      for (let i = 0; i < categoryListIncome.length; i++) {
        if (categoryListIncome[i].name === categoryFrom) {
          categoryListIncome[i].sum = categoryListIncome[i].sum - amount
          break
        }
    }
    setCategoryListIncome(categoryListIncome)
  }

  function callback (to, amount) {
    setModalActive(true)

    // console.log(to, amount)
  }

  return (    
    <div className="app">
      <SummaryBlock sumData={sumData} setSumData={setSumData}/>
      <CategoryList 
        group="income" 
        categoryFrom={categoryFrom}
        setCategoryFrom={setCategoryFrom}
        setCategoryTo={setCategoryTo}
        
        clbAddOperation={addOperation}
        callback={callback}
        categoryList={categoryListIncome}
        setCategoryList={setCategoryListExpense}
      />
      <hr style={{margin: '15px 0 15px 0'}}/>
      <CategoryList 
        group="expense" 
        categoryFrom={categoryFrom}
        setCategoryFrom={setCategoryFrom}   
        setCategoryTo={setCategoryTo}
        
        clbAddOperation={addOperation}
        callback={callback}
        categoryList={categoryListExpense}
        setCategoryList={setCategoryListIncome}
      />
      <Modal active={modalActive} setActive={setModalActive}>
          <div>Введите сумму:</div>
          <input className="amount"/>
          <button onClick={addOperation}>Добавить</button>
      </Modal>

    </div>
  );
}

export default App;
